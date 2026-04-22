mod scorer;
mod optimizer;

use tauri::Emitter;
use std::time::Duration;
use tokio::time::sleep;
use std::collections::HashMap;
use crate::optimizer::SimulatedAnnealing;
use crate::scorer::{Scorer, Weights};

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[tauri::command]
async fn run_optimization(handle: tauri::AppHandle, steps: usize, t_start: f32, t_end: f32, cooling_strategy: String, weights: Weights) -> String {
    // Mock data for frequencies (simplified English)
    let mut unigrams = HashMap::new();
    let mut bigrams = HashMap::new();
    let mut trigrams = HashMap::new();

    // Fill some basics for demonstration
    unigrams.insert("e".to_string(), 12.0);
    unigrams.insert("t".to_string(), 9.0);
    unigrams.insert("a".to_string(), 8.0);
    bigrams.insert("th".to_string(), 3.5);
    bigrams.insert("he".to_string(), 3.0);
    bigrams.insert("in".to_string(), 2.5);

    let scorer = Scorer::new(unigrams, bigrams, trigrams, weights);
    let optimizer = SimulatedAnnealing::new(scorer);

    let mut current_layout = [0usize; 30];
    for i in 0..30 { current_layout[i] = i; }

    // Run in chunks to emit updates
    let chunks = 20;
    let steps_per_chunk = steps / chunks;
    let mut best_layout = current_layout;
    let mut last_score = 999.0;

    for chunk in 0..chunks {
        // In a real run, we'd use the previous layout
        let (new_layout, new_score) = optimizer.run(best_layout, steps_per_chunk, t_start, t_end);
        best_layout = new_layout;
        last_score = new_score;

        // Convert layout indices to string representation
        let mut layout_str = String::new();
        for (i, &idx) in best_layout.iter().enumerate() {
            let c = crate::scorer::CHARS.chars().nth(idx).unwrap_or('?');
            layout_str.push(c);
            layout_str.push(' ');
            if (i + 1) % 10 == 0 && i < 29 {
                layout_str.push('\n');
            }
        }

        let _ = handle.emit("best_layout_found", serde_json::json!({
            "layout": layout_str.trim(),
            "score": last_score,
            "progress": (chunk + 1) as f32 / chunks as f32
        }));

        // Allow some UI breathing room
        sleep(Duration::from_millis(100)).await;
    }

    // Return final result
    let mut final_str = String::new();
    for (i, &idx) in best_layout.iter().enumerate() {
        let c = crate::scorer::CHARS.chars().nth(idx).unwrap_or('?');
        final_str.push(c);
        final_str.push(' ');
        if (i + 1) % 10 == 0 && i < 29 {
            final_str.push('\n');
        }
    }
    final_str.trim().to_string()
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![greet, run_optimization])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
