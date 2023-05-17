#include <stdio.h>
#include <string.h>

#ifndef FILEPROC_H
#define FILEPROC_H

// Error messages
#define FILEPROC_ERR_FILE			"\nFile Corrupt or Missing:"
#define FILEPROC_EXIT				"\nProgram exiting with code"
#define FILEPROC_INVALID_INPUT		"\nInvalid Input, Line"
#define FILEPROC_INVALID_MATCH		"\nInvalid Match, Line"

static char fileproc_buffer[256];
static char fileproc_line_number;
static char fileproc_filename[32];

FILE * OpenFile(char fname[])
{
	fileproc_line_number = 0;
	strcpy(fileproc_filename, fname);
	return fopen(fileproc_filename, "r");
}

char * GetLine()
{
	return fileproc_buffer;
}

int ReadLine(FILE * fp)
{
	fileproc_line_number++;
	if (fgets(fileproc_buffer, 255, fp) == NULL)
	{
		// end of file or error
		return 0;
	}
		
	return 1;

}

void FileError()
{
	
	printf( "%s %s\n", FILEPROC_ERR_FILE, fileproc_filename);
	exit(1);
}

void FormatError()
{

	printf( "%s\n%s %ld\n%s\n", 
		fileproc_filename, 
		FILEPROC_INVALID_INPUT, 
		fileproc_line_number, 
		fileproc_buffer);
	exit(1);
}

void MatchError()
{

	printf( "%s\n%s %ld\n%s\n", 
		fileproc_filename, 
		FILEPROC_INVALID_MATCH, 
		fileproc_line_number, 
		fileproc_buffer);
	getchar();
	exit(1);
}

#endif

