@echo off
echo [INFO] Compiling C++ files...

cl /std:c++17 /EHsc /MD /LD ^
  /I"C:\vcpkg\installed\x64-windows\include" ^
  /I"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8\include" ^
  /I"cpp" ^
  /I"cuda" ^
  /c cpp\dir_tag.cpp cpp\parse_csv.cpp cpp\trajectory.cpp cpp\fishing_score.cpp /Fo:lib\

echo [INFO] Linking with CUDA...

nvcc -ccbin "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.43.34808\bin\Hostx64\x64" ^
  -shared -o bin\OmniBase.dll cuda\kernel.cu lib\dir_tag.obj lib\parse_csv.obj lib\trajectory.obj lib\fishing_score.obj ^
  -I"C:\vcpkg\installed\x64-windows\include" ^
  -I"cpp" ^
  -I"cuda" ^
  -L"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8\lib\x64" -lcudart ^
  -Xcompiler "/MD /LD /std:c++17" --expt-relaxed-constexpr -std=c++17 -gencode arch=compute_80,code=sm_80

echo [INFO] ✅ Build complete. DLL output to bin\OmniBase.dll
pause


