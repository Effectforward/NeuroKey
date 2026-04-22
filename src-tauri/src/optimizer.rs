use rand::RngExt;
use rand::rng;
use crate::scorer::{Scorer, NUM_KEYS};

pub struct SimulatedAnnealing {
    pub scorer: Scorer,
}

impl SimulatedAnnealing {
    pub fn new(scorer: Scorer) -> Self {
        SimulatedAnnealing { scorer }
    }

    pub fn run(&self, initial_layout: [usize; 30], steps: usize, t_start: f32, t_end: f32) -> ([usize; 30], f32) {
        let mut current_layout = initial_layout;
        let mut pos_of = [0usize; 30];
        for (p, &c) in current_layout.iter().enumerate() {
            pos_of[c] = p;
        }

        let mut current_score = self.scorer.full_score(&current_layout);
        let mut best_layout = current_layout;
        let mut best_score = current_score;

        let mut rng = rng();

        for step in 0..steps {
            let t = t_start * (t_end / t_start).powf(step as f32 / steps as f32);

            // Mutate: Swap two random keys
            let p1 = rng.random_range(0..NUM_KEYS);
            let p2 = rng.random_range(0..NUM_KEYS);
            if p1 == p2 { continue; }

            let delta = self.scorer.delta_score(&current_layout, &pos_of, p1, p2);

            if delta < 0.0 || rng.random_bool((-delta / t).exp() as f64) {
                // Accept swap
                let c1 = current_layout[p1];
                let c2 = current_layout[p2];
                current_layout.swap(p1, p2);
                pos_of[c1] = p2;
                pos_of[c2] = p1;
                current_score += delta;

                if current_score < best_score {
                    best_score = current_score;
                    best_layout = current_layout;
                }
            }
        }

        (best_layout, best_score)
    }
}
