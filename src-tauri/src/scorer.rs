use std::collections::HashMap;

pub const CHARS: &str = "abcdefghijklmnopqrstuvwxyz.,';";
pub const NUM_KEYS: usize = 30;

pub const EFFORT: [f32; 30] = [
    3.0, 2.4, 2.0, 1.8, 2.2,   2.2, 1.8, 2.0, 2.4, 3.0,
    1.5, 1.1, 1.0, 1.0, 1.3,   1.3, 1.0, 1.0, 1.1, 1.5,
    3.5, 2.8, 2.5, 1.9, 3.0,   3.0, 1.9, 2.5, 2.8, 3.5,
];

pub const FINGER: [u8; 30] = [
    0, 1, 2, 3, 3,   4, 4, 5, 6, 7,
    0, 1, 2, 3, 3,   4, 4, 5, 6, 7,
    0, 1, 2, 3, 3,   4, 4, 5, 6, 7,
];

pub const HAND: [u8; 30] = [
    0, 0, 0, 0, 0,   1, 1, 1, 1, 1,
    0, 0, 0, 0, 0,   1, 1, 1, 1, 1,
    0, 0, 0, 0, 0,   1, 1, 1, 1, 1,
];

pub const COL: [u8; 30] = [
    0, 1, 2, 3, 4,   5, 6, 7, 8, 9,
    0, 1, 2, 3, 4,   5, 6, 7, 8, 9,
    0, 1, 2, 3, 4,   5, 6, 7, 8, 9,
];

#[derive(Clone, serde::Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Weights {
    pub sfb: f32,
    pub roll_bonus: f32,
    pub effort: f32,
    pub hand_bias: f32,
    pub outward_penalty: f32,
}

impl Default for Weights {
    fn default() -> Self {
        Weights {
            sfb: 10.0,
            roll_bonus: 3.5,
            effort: 1.0,
            hand_bias: 0.5,
            outward_penalty: 0.5,
        }
    }
}

pub struct Scorer {
    pub uni: Vec<f32>,
    pub bi: Vec<Vec<f32>>,
    pub tri: HashMap<(usize, usize, usize), f32>,
    pub weights: Weights,
}

impl Scorer {
    pub fn new(unigrams: HashMap<String, f32>, bigrams: HashMap<String, f32>, trigrams: HashMap<String, f32>, weights: Weights) -> Self {
        let mut char_to_idx = HashMap::new();
        for (i, c) in CHARS.chars().enumerate() {
            char_to_idx.insert(c, i);
        }

        let n_chars = CHARS.len();
        let mut uni = vec![0.0; n_chars];
        for (c_str, freq) in unigrams {
            if let Some(c) = c_str.chars().next() {
                if let Some(&idx) = char_to_idx.get(&c) {
                    uni[idx] = freq;
                }
            }
        }

        let mut bi = vec![vec![0.0; n_chars]; n_chars];
        for (gram, freq) in bigrams {
            let chars: Vec<char> = gram.chars().collect();
            if chars.len() == 2 {
                if let (Some(&i), Some(&j)) = (char_to_idx.get(&chars[0]), char_to_idx.get(&chars[1])) {
                    bi[i][j] = freq;
                }
            }
        }

        let mut tri = HashMap::new();
        for (gram, freq) in trigrams {
            let chars: Vec<char> = gram.chars().collect();
            if chars.len() == 3 {
                if let (Some(&i), Some(&j), Some(&k)) = (char_to_idx.get(&chars[0]), char_to_idx.get(&chars[1]), char_to_idx.get(&chars[2])) {
                    tri.insert((i, j, k), freq);
                }
            }
        }

        Scorer { uni, bi, tri, weights }
    }

    pub fn full_score(&self, layout: &[usize; 30]) -> f32 {
        let mut score = 0.0;
        let mut pos_of = [0usize; 30];
        for (p, &c) in layout.iter().enumerate() {
            pos_of[c] = p;
        }

        // 1. Effort (Unigrams)
        for c in 0..30 {
            score += self.uni[c] * EFFORT[pos_of[c]] * self.weights.effort;
        }

        // 2. Bigrams (SFB, Hand Balance, Rolls)
        for i in 0..30 {
            for j in 0..30 {
                let freq = self.bi[i][j];
                if freq == 0.0 { continue; }

                let p1 = pos_of[i];
                let p2 = pos_of[j];

                // SFB
                if FINGER[p1] == FINGER[p2] && HAND[p1] == HAND[p2] {
                    score += freq * self.weights.sfb;
                }

                // Rolls
                if HAND[p1] == HAND[p2] && FINGER[p1] != FINGER[p2] {
                    if self.is_inward_roll(p1, p2) {
                        score -= freq * self.weights.roll_bonus;
                    } else {
                        score += freq * self.weights.outward_penalty;
                    }
                }
            }
        }

        // 3. Hand Balance
        let mut left_usage = 0.0;
        let total_usage: f32 = self.uni.iter().sum();
        if total_usage > 0.0 {
            for c in 0..30 {
                if HAND[pos_of[c]] == 0 {
                    left_usage += self.uni[c];
                }
            }
            let left_ratio = left_usage / total_usage;
            score += (left_ratio - self.weights.hand_bias).abs() * 50.0;
        }

        score
    }

    pub fn delta_score(&self, layout: &[usize; 30], pos_of: &[usize; 30], pos_a: usize, pos_b: usize) -> f32 {
        let mut delta = 0.0;
        let char_a = layout[pos_a];
        let char_b = layout[pos_b];

        // 1. Unigram Delta (Effort)
        delta -= self.uni[char_a] * EFFORT[pos_a] * self.weights.effort;
        delta -= self.uni[char_b] * EFFORT[pos_b] * self.weights.effort;
        delta += self.uni[char_a] * EFFORT[pos_b] * self.weights.effort;
        delta += self.uni[char_b] * EFFORT[pos_a] * self.weights.effort;

        // 2. Bigram Delta
        for other_c in 0..30 {
            if other_c == char_a || other_c == char_b { continue; }
            let other_p = pos_of[other_c];

            delta += self.bigram_pair_delta(other_c, other_p, char_a, pos_a, pos_b);
            delta += self.bigram_pair_delta(other_c, other_p, char_b, pos_b, pos_a);
        }
        
        delta -= self.bi[char_a][char_b] * self.pair_penalty(pos_a, pos_b);
        delta -= self.bi[char_b][char_a] * self.pair_penalty(pos_b, pos_a);
        delta += self.bi[char_a][char_b] * self.pair_penalty(pos_b, pos_a);
        delta += self.bi[char_b][char_a] * self.pair_penalty(pos_a, pos_b);

        delta
    }

    fn bigram_pair_delta(&self, c1: usize, p1: usize, c2: usize, p2_old: usize, p2_new: usize) -> f32 {
        let mut d = 0.0;
        let freq12 = self.bi[c1][c2];
        if freq12 > 0.0 {
            d -= freq12 * self.pair_penalty(p1, p2_old);
            d += freq12 * self.pair_penalty(p1, p2_new);
        }
        let freq21 = self.bi[c2][c1];
        if freq21 > 0.0 {
            d -= freq21 * self.pair_penalty(p2_old, p1);
            d += freq21 * self.pair_penalty(p2_new, p1);
        }
        d
    }

    fn pair_penalty(&self, p1: usize, p2: usize) -> f32 {
        let mut p = 0.0;
        if FINGER[p1] == FINGER[p2] && HAND[p1] == HAND[p2] {
            p += self.weights.sfb;
        }
        if HAND[p1] == HAND[p2] && FINGER[p1] != FINGER[p2] {
            if self.is_inward_roll(p1, p2) {
                p -= self.weights.roll_bonus;
            } else {
                p += self.weights.outward_penalty;
            }
        }
        p
    }

    fn is_inward_roll(&self, p1: usize, p2: usize) -> bool {
        let c1 = COL[p1];
        let c2 = COL[p2];
        if HAND[p1] == 0 { // Left
            c2 > c1
        } else { // Right
            c2 < c1
        }
    }
}
