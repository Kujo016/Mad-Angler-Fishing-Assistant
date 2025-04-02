#pragma once
#include "../cuda/kernel.cuh"
#include <vector>
#include <string>

extern "C" __declspec(dllexport) void get_predicted_quadrants(const char* traj_path, char* buffer, int buffer_size);
extern "C" __declspec(dllexport) void __stdcall compute_weather_trajectory_bin(const char* input_bin_path, const char* output_bin_path);
int quadrant_to_index(char q);
std::vector<char> extract_quadrant_sequence(const std::string& filepath);
int count_pattern(const std::vector<char>& seq, const std::vector<char>& pattern);
std::vector<std::vector<float>> build_transition_matrix(const std::vector<char>& seq);
float score_transition_matrix(const std::vector<std::vector<float>>& matrix);
float score_patterns(const std::vector<char>& seq);
float score_dummy(float weight);
std::vector<TrajectoryPoint> predict_next_trajectory(const std::vector<TrajectoryPoint>& past_data, int future_steps = 10);
char calculate_quadrant(float dx, float dy);
float compute_fishing_score(const std::string& traj_bin);
extern "C" __declspec(dllexport) float __stdcall get_fishing_score(const char* traj_bin_path);
