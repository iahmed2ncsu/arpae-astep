// TrafAssign.h : generate the traffic assignment
// n, s, r, and sometimes i, j and k are internal node numbers
// nnum is an external number that refers to a specific node
// z, zo and zd are internal zone numbers
// znum is an external number that refers to a specific zone 
// znode is the external node number for a specific zone
// zn is the interal node number for the zone
// a is an internal arc number
// lnum is an external number that refers to a specific link

#pragma once

#include <iostream>
#include <math.h>
#include <stdio.h>
#include "FileProc.h"

float theta;
float cMax;
long temp[40000], scnd[40000], Indx[40000];

long aMax, cPerm, cminflag;
long lNum[40000], fr[40000], to[40000];
long nDir[40000], aChk[40000], aWrk[40000];
float w[40000], ls[40000], lsr[40000];
float aCost[40000], uCoef[40000], aFlow[40000];

// nNum is more than twice as large, so are temp and NodeIdx, so the unique node numbers can be found
long nMax, nlMax, ipt, nIpt, nDup[18000];
long nNum[36000], nChk[18000], nLst[18000];
long nip[18000], ip[18000][10], nop[18000], op[18000][10];
long odnode[18000];

long zMax;
long zNum[18000], zNode[18000], zn[9000];
long idx[9000][18000];
float cs[9000][18000], cr[9000][18000];

long odMax, odMaxInput;
long zo[9000], zd[9000];
long nzo[9000], nzd[9000];
float odFlow[9000];
float avgCost[9000];

FILE* infile;
FILE* outfile;

// Node number search routine
// Assumes the node numbers are in ascending order
long nxref(long npass)
{
	long nFind, done;
	float x, dx, sgn;

	done = 0;
	x = 0;
	dx = (float)nMax;
	sgn = 1;

	while (done == 0)
	{
		dx = (float)(dx / 2.0);
		if (dx < 0.25) return (-1);
		x = x + sgn * dx;
		nFind = (long)(x + 0.5);
		if (npass < nNum[nFind]) sgn = -1;
		if (npass == nNum[nFind]) done = 1;
		if (npass > nNum[nFind]) sgn = 1;
	}

	return (nFind);
}

// Sort the node numbers into ascending order
// remove duplicates, and save the results
void GetNodes(void)
{
	long i, j, jump, done;
	long hold1, hold2;
	long cnode;

	for (i = 1; i <= nMax; i++)
	{
		temp[i] = nNum[i];
		Indx[i] = i;
    }

	jump = (long)((float)nMax / 2.0);

	while (jump >= 1)
    {
		done = 0;
		while (done != 1)
		{
			done = 1;
			for (i = 1; i <= nMax - jump; i++)
			{
				j = i + jump;
				if (temp[i] > temp[j])
				{
					hold1 = temp[i];
					temp[i] = temp[j];
					temp[j] = hold1;
					hold2 = Indx[i];
					Indx[i] = Indx[j];
					Indx[j] = hold2;
					done = 0;
				}
			}
		}
		jump = (long)((float)jump / 2.0);
	}

	// put the node numbers in ascending order 
	for (i = 1; i <= nMax; ++i) temp[i] = nNum[Indx[i]];
   
	// place the unique node numbers back into the original node array;
	j = 0;
	cnode = -1;
	for (i = 1; i <= nMax; i++)
	{
		if (temp[i] != cnode)
		{
			j++;
			nNum[j] = temp[i];
			cnode = temp[i];
			nDup[j] = 1;
		}
		else
		{
			nDup[j] = nDup[j] + 1;
		}
	}

	// reset nMax;
	nMax = j;

	// output the node array to a textfile;
	outfile = fopen("nodes.txt", "w");
	for (i = 1; i <= nMax; i++)
		fprintf(outfile, "%d\t%d\n", nNum[i], nDup[i]);
}

// Get Node and Arc Data from Links
// Need to use internal node numbers for n1 and n2
// Those numbers are added to the arc array after the
// node numbers are put in sequence and duplicates removed
void GetLinkData(void)
{
	long n1, n2;
	long mid, mfr, mto;
	float mabcost, mbacost;
	long a, nval;
	char ifname[10] = "links.txt";

	// get node data first

	printf("Getting node data\n");

	nMax = 0;
	if ((infile = OpenFile(ifname)) == NULL) FileError();

	while (ReadLine(infile))
	{
		nval = sscanf(GetLine(), "%d%d%d%f%f", &mid, &mfr, &mto, &mabcost, &mbacost);
		if (nval != 5) FormatError();

		nMax++;
		nNum[nMax] = mfr;
		nMax++;
		nNum[nMax] = mto;
	}

	fclose(infile);

	GetNodes();

	printf("Getting arc data\n");

	aMax = 0;
	if ((infile = OpenFile(ifname)) == NULL) FileError();

	while (ReadLine(infile))
	{
		nval = sscanf(GetLine(), "%d%d%d%f%f", &mid, &mfr, &mto, &mabcost, &mbacost);
		if (nval != 5) FormatError();

		n1 = nxref(mfr);
		n2 = nxref(mto);
			
		aMax++;
		lNum[aMax] = mid;
		aCost[aMax] = mabcost;
		fr[aMax] = n1;
		to[aMax] = n2;
		nDir[aMax] = 1;
		nop[n1]++;
		op[n1][nop[n1]] = aMax;
		nip[n2]++;
		ip[n2][nip[n2]] = aMax;
	
		aMax++;
		aCost[aMax] = mbacost;
		lNum[aMax] = mid;
		fr[aMax] = n2;
		to[aMax] = n1;
		nDir[aMax] = -1;
		nop[n2]++;
		op[n2][nop[n2]] = aMax;
		nip[n1]++;
		ip[n1][nip[n1]] = aMax;
	}

	for (a = 1; a <= aMax; ++a)
		aFlow[a] = 0;

	fclose(infile);

}

// Zone number search routine
// Assumes the zone numbers are in ascending order
long zxref(long zpass)
{
	long zFind, done;
	float x, dx, sgn;

	done = 0;
	zFind = 0;
	x = 0;
	dx = (float)zMax;
	sgn = 1;

	while (done == 0)
	{
		dx = (float)(dx / 2.0);
		if (dx < 0.25) return (-1);
		x = x + sgn * dx;
		zFind = (long)(x + 0.5);
		if (zpass < zNum[zFind]) sgn = -1;
		if (zpass == zNum[zFind]) done = 1;
		if (zpass > zNum[zFind]) sgn = 1;
	}

	return (zFind);
}

// Sort the zone numbers into ascending order
// remove the duplicates, and save the results
void GetZones(void)
{
	long i, j, jump, done;
	long hold1, hold2;
	long cnode;

	for (i = 1; i <= zMax; i++)
	{
		temp[i] = zNum[i];
		Indx[i] = i;
    }

	jump = (long)((float)zMax / 2.0);

	while (jump >= 1)
	{
		done = 0;
		while (done != 1)
		{
			done = 1;
			for (i = 1; i <= zMax - jump; i++)
			{
				j = i + jump;
				if (temp[i] > temp[j])
				{
					hold1 = temp[i];
					temp[i] = temp[j];
					temp[j] = hold1;
					hold2 = Indx[i];
					Indx[i] = Indx[j];
					Indx[j] = hold2;
					done = 0;
				}
			}
		}
		jump = (long)((float)jump / 2.0);
	}

	// put the zone number and zone node data in ascending order by znum 
	for (i = 1; i <= zMax; i++) temp[i] = zNum[Indx[i]];
	for (i = 1; i <= zMax; i++) scnd[i] = zNode[Indx[i]];
  
	// identify the unique zone numbers and place them and the zone nodes 
	// back into their original arrays;
	j = 0;
	cnode = -1;
	for (i = 1; i <= zMax; i++)
	{
		if (temp[i] != cnode)
		{
			j++;
			zNum[j] = temp[i];
			zNode[j] = scnd[i];
			zn[j] = nxref(zNode[j]);
			cnode = temp[i];
			nDup[j] = 1;
		}
		else
		{
			nDup[j] = nDup[j] + 1;
		}
	}

    // reset zMax;
    zMax = j;

	// store the node array to a textfile;
	outfile = fopen("zones.txt", "w");
	for (i = 1; i <= zMax; i++)
		fprintf(outfile, "%d\t%d\t%d\t%d\n", zNum[i], zNode[i], zn[i], nDup[i]);
}

//Get zone numbers and flow data;
//The zone numbers, not node numbers, need to be cross referenced to the internal zone numbers
void GetFlowData(void)
{
	long nval;
	long mznumo, mznumd, mfafo, mfafd, mno, mnd, mfrao, mfrad;
	float mflow;
	char ifname[12] = "odflows.txt";

	// Get OD flow data
	//zOrig	zDest	FAF_O	FAF_D	netNodeO	netNodeD	FRA_O	FRA_D	fTons(K)
	//301	300		532		531		191			300			304539	307557	14817.7168
	//136	138		221		223		5918		6300		390084	395671	7907.360352

	printf("Getting zone data\n");

	odMax = 1;
	zMax = 0;
	if ((infile = OpenFile(ifname)) == NULL) FileError();

	while (ReadLine(infile) && odMax <= odMaxInput)
	{
		nval = sscanf(GetLine(), "%d%d%d%d%d%d%d%d%f", &mznumo, &mznumd, &mfafo, &mfafd, &mno, &mnd, &mfrao, &mfrad, &mflow);
		if (nval != 9) FormatError();

		++zMax;
		zNum[zMax] = mznumo;
		zNode[zMax] = mno;
		++zMax;
		zNum[zMax] = mznumd;
		zNode[zMax] = mnd;
		++odMax;
		// do not save the value of odMax during this pass through the data
	}

	fclose(infile);

	GetZones();

	printf("Getting flow data\n");

	odMax = 1;
	if ((infile = OpenFile(ifname)) == NULL) FileError();

	while (ReadLine(infile) && odMax <= odMaxInput)
	{
		nval = sscanf(GetLine(), "%d%d%d%d%d%d%d%d%f", &mznumo, &mznumd, &mfafo, &mfafd, &mno, &mnd, &mfrao, &mfrad, &mflow);
		if (nval != 9) FormatError();

		zo[odMax] = zxref(mznumo);
		zd[odMax] = zxref(mznumd);
		nzo[odMax] = nxref(mno);
		nzd[odMax] = nxref(mnd);
		odFlow[odMax] = mflow;
		++odMax;
	}

	fclose(infile);

	if (odMaxInput < odMax) odMax = odMaxInput;
}

// Initialization Routine
void Initialize(void)
{

	long count = 0;
	char ifname[14] = "luparams.txt";

	if ((infile = OpenFile(ifname)) == NULL) FileError();

	//    EXP     CMAX		cMinFlag	odMax;
	//   1.00    14000.0		0		2000;

	if (!ReadLine(infile)) FormatError();
	count = sscanf(GetLine(), "%f%f%d%d", &theta, &cMax, &cminflag, &odMaxInput);

	printf("Initialization subroutine %f\t%f\t%d\t%d\n", theta, cMax, cminflag, odMaxInput);

	if (count != 4) FormatError();

	fclose(infile);

	GetLinkData();
	GetFlowData();
}

// Generate the Minimum Cost Values
// ZO-----S----R----ZD;
void MinCost(void)
{
	long od, m;
	long z1, z2, nDone, nAct;
	long na, naNext;
	long j, jNext, k;
	long s, r, a;
	long active[50000]{};
	float test;

	printf("MinCost subroutine\n");

	if (cminflag == 1) outfile = fopen("mcost.txt", "w");
	
	printf("Forward and backward costs\n");

	for (od = 1; od <= odMax; ++od)
	{
		z1 = zo[od];
		z2 = zd[od];

		s = zn[z1];
		s = nzo[od];

		for (j = 1; j <= nMax; ++j)
		{
			idx[od][j] = 0;
			cs[od][j] = cMax;
			active[j] = -1;
		}

		s = nzo[od];
		cs[od][s] = 0;
		nAct = 1;
		active[nAct] = s;

		nDone = 0;
		while ((nDone < nMax) && (nAct > 0))
		{
			test = cMax;
			for (na = 1; na <= nAct; ++na)
			{
				j = active[na];
				if (cs[od][j] < test)
				{
					jNext = j;
					naNext = na;
					test = cs[od][j];
				}
			}

			j = jNext;
			if (nAct > 0)
			{
				active[naNext] = active[nAct];
				active[nAct] = -1;
				nAct = nAct - 1;
				if ((j == s) || (odnode[j] == 0))
				{
					for (m = 1; m <= nop[j]; ++m)
					{
						a = op[j][m];
						k = to[a];
						if (cs[od][k] >= cMax)
						{
							nAct++;
							active[nAct] = k;
						}
						if (cs[od][j] + aCost[a] < cs[od][k])
						{
							cs[od][k] = cs[od][j] + aCost[a];
						}
					}
				}

				nDone++;
				idx[od][nDone] = j;
			}
		}

		// printf("FwdCost: z \t%d\n", z);
		// s as index because this evaluation is for the s end of each arc

		if (cminflag == 1)
		{
			for (s = 1; s <= nMax; ++s)
				if (cs[od][s] < cMax)
					fprintf(outfile, "%d\t%d\t%f\n", zo[od], nNum[s], cs[od][s]);
		}

		for (j = 1; j <= nMax; ++j)
		{
			cr[od][j] = cMax;
			active[j] = -1;
		}

		r = zn[z2];
		r = nzd[od];
		nDone = 0;
		cr[od][r] = 0;
		nAct = 1;
		active[nAct] = r;

		while ((nDone < nMax) && (nAct > 0))
		{
			test = cMax;
			for (na = 1; na <= nAct; ++na)
			{
				j = active[na];
				if (cr[od][j] < test)
				{
					jNext = j;
					naNext = na;
					test = cr[od][j];
				}
			}

			j = jNext;
			if (nAct > 0)
			{
				active[naNext] = active[nAct];
				active[nAct] = -1;
				nAct = nAct - 1;
				if ((j == r) || (odnode[j] == 0))
				{
					for (m = 1; m <= nip[j]; ++m)
					{
						a = ip[j][m];
						k = fr[a];
						if (cr[od][k] >= cMax)
						{
							nAct = nAct + 1;
							active[nAct] = k;
						}
						if (cr[od][j] + aCost[a] < cr[od][k])
						{
							cr[od][k] = cr[od][j] + aCost[a];
						}
					}
				}
				nDone++;
			}
		}

		// printf("BwdCost: z \t%d\n", z);
		// r as index because this evaluation is for the r end of each arc
		if (cminflag == 1)
		{
			for (r = 1; r <= nMax; ++r)
				if (cr[od][r] <cMax)
					fprintf(outfile, "%d\t%d\t%f\n", zd[od], nNum[r], cr[od][r]);
		}
	}
}

// Subroutine SLikes
void SLikes(long od)
{
	long i, j, k, a;
	float ta;

	k = 0;

	for (a = 1; a <= aMax; ++a)
	{
		//  S-----I----A----J----R;
		i = fr[a];
		j = to[a];
		ta = aCost[a];
		
		if (cs[od][j] >= cs[od][i])
		{
			ls[a] = (float)exp(theta * (cs[od][j] - cs[od][i] - ta));
			k++;
			aChk[k] = a;
		}
		else
		{
			ls[a] = 0;
		}
	}
	aChk[k + 1] = -1;
}

// Subroutine RLikes
void RLikes(long od)
{
	long i, j, k, m, a;

	m = 0;
	k = 1;
	a = aChk[k];

	while ((a > 0) && (k <= aMax))
	{
		//  S-----I----A----J----R;
		i = fr[a];
		j = to[a];


		if (cr[od][i] >= cr[od][j])
		{
			lsr[a] = ls[a];
			nChk[j] = 1;
			m++;
			aWrk[m] = a;
		}
		else
		{
			lsr[a] = 0;
		}
		k++;
		a = aChk[k];
	}

	aWrk[m + 1] = -1;
}

// Subroutine NLstGen
void NLstGen(long od)
{
	long i, k, m;

	m = 0;
	k = 1;
	i = idx[od][k];
	while (i > 0)
	{
		if (nChk[i] > 0)
		{
			m++;
			nLst[m] = i;
		}
		k++;
		i = idx[od][k];
	}

	nlMax = m;
}

// Subroutine Weights(s)
void Weights(long s)
{
	long a, i, j, k;
	float postm;

	for (k = 1; k <= nlMax - 1; ++k)
	{
		i = nLst[k];
		if (i == s)
		{
			postm = 1;
		}
		else
		{
			j = 1;
			postm = 0;
			while (j <= nip[i])
			{
				a = ip[i][j];
				postm = postm + w[a];
				j++;
			}
		}
		j = 1;
		while (j <= nop[i])
		{
			a = op[i][j];
			w[a] = lsr[a] * postm;
			j++;
		}
	}
}

// Subroutine Factors
void Factors(long r)
{
	long a, i, j, k, kBak;
	float numer, denom;

	for (k = 1; k <= nlMax - 1; ++k)
	{
		kBak = nlMax + 1 - k;
		i = nLst[kBak];

		if (i == r)
		{
			numer = 1.0;
		}
		else
		{
			j = 1;
			numer = 0.0;
			while (j <= nop[i])
			{
				a = op[i][j];
				numer = numer + uCoef[a];
				j++;
			}
		}

		j = 1;
		denom = 0;
		while (j <= nip[i])
		{
			a = ip[i][j];
			denom = denom + w[a];
			j++;
		}

		j = 1;
		while (j <= nip[i])
		{
			a = ip[i][j];
			if (denom <= 0)
			{
				uCoef[a] = 0;
			}
			else
			{
				uCoef[a] = numer * (w[a] / denom);
			}
			j++;
		}
	}
}

// Generate utilization coefficients and link flows
// Internal node and arc numbers are used for z1, z2, and a
void GenCoefs(void)
{
	long k, a, na, iuc;
	long s, r, z1, z2;
	long od;
	long lk;

	printf("Generating flows and arc use\n");

	// outfile = fopen("coef.txt", "w");

	for (od = 1; od <= odMax; ++od)
	{
		z1 = zo[od];
		z2 = zd[od];
		// printf("GenCoefs: %d\t%d\t%d\n", od, zNum[z1], zNum[z2]);
	
		s = zn[z1];
		s = nzo[od];
		SLikes(od);

		avgCost[od] = 0;

		r = zn[z2];
		r = nzd[od];

		if (s != r)
		{
			for (k = 1; k <= nMax; ++k) nChk[k] = 0;
			nChk[s] = 1;

			for (a = 1; a <= aMax; ++a)
			{
				lsr[a] = 0;
				w[a] = 0;
				uCoef[a] = 0;
			}

			RLikes(od);
			NLstGen(od);
			Weights(s);
			Factors(r);

			k = 1;
			a = aWrk[k];
			while ((a > 0) && (k <= aMax))
			{
				avgCost[od] = avgCost[od] + uCoef[a] * aCost[a];
				na = nDir[a] * lNum[a];
				iuc = (long)(100.0 * uCoef[a] + 0.5);
				aFlow[a] = aFlow[a] + uCoef[a] * odFlow[od];
//				if (uCoef[a] > 0)
//				{
//					fprintf(outfile, "%d\t%d\t%d\t%d\t%8.4f\t%8.2f\n", od, zNum[z1], zNum[z2], na, uCoef[a], aFlow[a]);
//				}

				k++;
				a = aWrk[k];
			}
		}
	}

	outfile = fopen("lkflow.txt", "w");
	for (a = 2; a <= aMax; a = a + 2)
	{
	//	if ((aFlow[a - 1] > 0) || (aFlow[a] > 0))
		fprintf(outfile, "%d\t%8.3f\t%8.3f\n", lNum[a], aFlow[a - 1], aFlow[a]);
	}
}

// Output the average distance matrix
void OutputAvgCost(void)
{
	long od, orig, dest;
	long r, s;

	printf("Recording average costs and ts and tr for each od pair\n");


	outfile = fopen("avgcost.txt", "w");

	for (od = 1; od <= odMax; ++od)
	{
		orig = zNum[zo[od]];
		dest = zNum[zd[od]];
		r = nzo[od];
		s = nzd[od];
 		fprintf(outfile, "%d\t%d\t%d\t%8.3f\t%8.3f\t%8.3f\n", od, orig, dest, cs[od][s], cr[od][r], avgCost[od]);
	}
}

//Finish all processing
void FinishUp(void)
{
	printf("Finishing up\n");

	_fcloseall();

}

//end of code