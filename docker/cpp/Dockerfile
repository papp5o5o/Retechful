FROM gcc:13
WORKDIR /judge
COPY sol.cpp .
RUN g++ -O2 -o sol sol.cpp
CMD ["./sol"]
