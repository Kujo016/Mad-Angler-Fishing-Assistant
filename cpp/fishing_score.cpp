#include "../cpp/trajectory.h"



// Constants for scoring
constexpr float MAX_SCORE = 100.0f;
constexpr float WEIGHTS[] = { 15.0f, 20.0f, 20.0f, 10.0f, 10.0f, 10.0f };

// Patterns that usually indicate good fishing
const std::vector<std::vector<char>> BITE_PATTERNS = {
    {'b'}, {'f', 'b'}, {'g', 'b'}, {'e', 'f', 'b'}
};

// Count pattern matches in sequence
int count_pattern(const std::vector<char>& seq, const std::vector<char>& pattern) {
    int count = 0;
    for (size_t i = 0; i + pattern.size() <= seq.size(); ++i) {
        if (std::equal(pattern.begin(), pattern.end(), seq.begin() + i))
            count++;
    }
    return count;
}

// Build a Markov Chain transition matrix
std::vector<std::vector<float>> build_transition_matrix(const std::vector<char>& seq) {
    std::vector<std::vector<int>> counts(9, std::vector<int>(9, 0));
    std::vector<std::vector<float>> matrix(9, std::vector<float>(9, 0.0f));

    for (size_t i = 1; i < seq.size(); ++i) {
        int prev = quadrant_to_index(seq[i - 1]);
        int curr = quadrant_to_index(seq[i]);
        counts[prev][curr]++;
    }
    for (int i = 0; i < 9; ++i) {
        int row_total = std::accumulate(counts[i].begin(), counts[i].end(), 0);
        if (row_total > 0) {
            for (int j = 0; j < 9; ++j) {
                matrix[i][j] = static_cast<float>(counts[i][j]) / row_total;
            }
        }
    }
    return matrix;
}

// Score the Markov Chain for useful transitions
float score_transition_matrix(const std::vector<std::vector<float>>& matrix) {
    float score = 0.0f;
    score += matrix[quadrant_to_index('d')][quadrant_to_index('g')] * 5.0f; // chaos to lift
    score += matrix[quadrant_to_index('g')][quadrant_to_index('b')] * 5.0f; // lift to ideal
    score += matrix[quadrant_to_index('e')][quadrant_to_index('f')] * 5.0f;
    score += matrix[quadrant_to_index('f')][quadrant_to_index('b')] * 5.0f;
    return std::min(score, WEIGHTS[1]);
}

// Score the pattern match
float score_patterns(const std::vector<char>& seq) {
    int total_hits = 0, total_possible = 0;
    for (const auto& pattern : BITE_PATTERNS) {
        int matches = count_pattern(seq, pattern);
        total_hits += matches;
        total_possible += std::max((int)seq.size() - (int)pattern.size() + 1, 0);
    }
    if (total_possible == 0) return 0.0f;
    float ratio = static_cast<float>(total_hits) / total_possible;
    return std::min(ratio * WEIGHTS[0], WEIGHTS[0]);
}

// TODO: Fill in with vector momentum, bias, etc.
float score_dummy(float weight) {
    return 0.8f * weight; // placeholder
}

// Main scoring function
float compute_fishing_score(const std::string& traj_bin) {
    auto seq = extract_quadrant_sequence(traj_bin);
    if (seq.empty()) return 0.0f;

    float bite_score = score_patterns(seq);
    auto matrix = build_transition_matrix(seq);
    float transition_score = score_transition_matrix(matrix);

    float momentum_score = score_dummy(WEIGHTS[2]);
    float direction_score = score_dummy(WEIGHTS[3]);
    float current_score = score_dummy(WEIGHTS[4]);
    float seasonal_score = score_dummy(WEIGHTS[5]);

    float total = bite_score + transition_score + momentum_score +
        direction_score + current_score + seasonal_score;
    return std::clamp(total, 0.0f, MAX_SCORE);
}

// Entry point
extern "C" __declspec(dllexport) float __stdcall get_fishing_score(const char* traj_bin_path) {
    return compute_fishing_score(std::string(traj_bin_path));
}
