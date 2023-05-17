// TrafAssign.cpp : Defines the entry point for the application.
//
/*
	Rail traffic assignment program 
*/
#include <stdio.h>
#include <chrono>
#include <stdlib.h>
#include <math.h>
#include "TrafAssign.h"

using namespace std;

int main()
{
	auto begin = std::chrono::high_resolution_clock::now();

	cout << "Program Generate Traffic Assignment\n" << endl;

	// atexit(FinishUp);

	Initialize();
	MinCost();
	GenCoefs();
	OutputAvgCost();
	FinishUp();

	auto end = std::chrono::high_resolution_clock::now();
	auto elapsed = std::chrono::duration_cast<std::chrono::nanoseconds>(end - begin);
	
	// store the execution time;
	outfile = fopen("xtime.txt", "w");
	fprintf(outfile, "Time measured: %.3f seconds.\n", elapsed.count() * 1e-9);

	return 0;
}
