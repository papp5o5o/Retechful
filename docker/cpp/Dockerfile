FROM gcc:13
RUN apt-get update && apt-get install -y python3 && rm -rf /var/lib/apt/lists/*
WORKDIR /judge
COPY docker/cpp/sol.cpp .
COPY runner/run_judge.py .
RUN g++ -O2 -o sol sol.cpp
CMD ["python3", "run_judge.py"]
