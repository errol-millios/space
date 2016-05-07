/*
 * Copyright (C) 1999  John Olsson
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
 */

/* This is the CGI version of the fractal generator. I haven't had time
 * to modify the old, ugly generator to include the perspective
 * transformations, etc. This code is provided as is, and, well, it's
 * mostly a big "hack" with nearly no comments.
 *
 * Version 1.1 : I fixed a bug which has haunted me for several months now.
 *               It was one of those "off by one" things. (I had forgotten
 *               to subtract 1 from an index, this caused a segmentation
 *               fault. Anyways *this* bug is fixed now, I hope there are
 *               no more. ;)
 */

#include    <limits.h>
#include    <stdio.h>
#include    <stdlib.h>
#include    <unistd.h>
#include    <time.h>
#include    <string.h>
#include    <math.h>


/* These define:s are for the GIF-saver... */
/* a code_int must be able to hold 2**BITS values of type int, and also -1 */
typedef int             code_int;

#ifdef SIGNED_COMPARE_SLOW
typedef unsigned long int count_int;
typedef unsigned short int count_short;
#else /*SIGNED_COMPARE_SLOW*/
typedef long int          count_int;
#endif /*SIGNED_COMPARE_SLOW*/

static void BumpPixel ( void );
static int GIFNextPixel ( void );
static void GIFEncode (FILE* fp, int GWidth, int GHeight, int GInterlace, int Background, int BitsPerPixel, int Red[], int Green[], int Blue[], char Transparent, char TransparentColor);
static void Putword ( int w, FILE* fp );
static void compress ( int init_bits, FILE* outfile );
static void output ( code_int code );
static void cl_block ( void );
static void cl_hash ( count_int hsize );
static void writeerr ( void );
static void char_init ( void );
static void char_out ( int c );
static void flush_char ( void );

/* My own definitions */
#ifndef PI
#define PI      3.141593
#endif

/* This value holds the maximum value rand() can generate
 *
 * RAND_MAX *might* be defined in stdlib.h, if it's not
 * you *might* have to change the definition of MAX_RAND...
 */
#ifdef RAND_MAX
#define MAX_RAND  RAND_MAX
#else
#define MAX_RAND  0x7FFFFFFF
#endif

#define SQUARE              0
#define MERCATOR            1
#define SPHERICAL           2
#define ORTHOGRAPHIC_NP     3
#define ORTHOGRAPHIC_SP     4
#define STEREOGRAPHIC_NP    5
#define STEREOGRAPHIC_SP    6
#define GNOMIC_NP           7
#define GNOMIC_SP           8
#define LAMBERT_AREAP_NP    9
#define LAMBERT_AREAP_SP   10


#define HEIGHT    0
#define RADIUS    1

void PrintError(char *, char *);

/* Function that generates the worldmap */
void GenerateSquareWorldMap();
void GenerateMercatorWorldMap();

/* 4-connective floodfill algorithm which I use for constructing
 *  the ice-caps.*/
void FloodFill4(int x, int y, int OldColor);

int             *WorldMapArray;
int             XRange = -1;
int             YRange = -1;
int             Radius = 0;
int             Diameter = 0;
int             RSquared = 0;
int             Histogram[256];
int             FilledPixels;
int             ScrollDistance = 0, ScrollDegrees;
int             ProjectionType = SQUARE;

int             Red[255]   = {0,0,0,0,0,0,0,0,34,68,102,119,136,153,170,187,
			     0,34,34,119,187,255,238,221,204,187,170,153,
			     136,119,85,68,
			     255,250,245,240,235,230,225,220,215,210,205,200,
			     195,190,185,180,175,0,0,0,0,0,0,
			     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
			     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
			     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
			     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
			     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
			     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
			     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
			     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
			     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
			     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
int             Green[255] = {0,0,17,51,85,119,153,204,221,238,255,255,255,
			     255,255,255,68,102,136,170,221,187,170,136,
			     136,102,85,85,68,51,51,34,
			     255,250,245,240,235,230,225,220,215,210,205,200,
			     195,190,185,180,175,0,0,0,0,0,0,
			     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
			     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
			     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
			     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
			     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
			     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
			     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
			     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
			     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
			     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
int             Blue[255]  = {0,68,102,136,170,187,221,255,255,255,255,255,
			     255,255,255,255,0,0,0,0,0,34,34,34,34,34,34,
			     34,34,34,17,0,
			     255,250,245,240,235,230,225,220,215,210,205,200,
			     195,190,185,180,175,0,0,0,0,0,0,
			     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
			     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
			     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
			     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
			     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
			     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
			     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
			     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
			     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
			     0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
float           YRangeDiv2, YRangeDivPI;
float           *SinIterPhi;

/*
 * This is the text that ends up in a comment-block in the GIF-file
 */
char        CommentText1[] = "This image was generated by the Fractal Worldmap Generator (1996) by John Olsson (johol@lysator.liu.se).\nI got the idea from the book \"The Science of Fractal Images\" by D. Saupe and H. Peitgen.\n\n";
char        CommentText2[] = "The program is in the public domain and you should be able to get a copy from my homepage http://www.lysator.liu.se/~johol/ or from ftp://ftp.funet.fi/pub/doc/games/roleplay/programs/mapping/worldgen.zip.\n\n";
char        CommentText3[] = "The following parameters were used to create this image:\n";
char        ImageInfo[512];

/*
 * Prints an errormessage
 */
void PrintError(char *message, char *opt)
{
    printf("Content-type: text/html\n\n");
    printf("<HTML>");
    printf("<BODY BACKGROUND = \"http://www.edu.isy.liu.se/~d91johol/images/background.gif\"\n");
    printf("      BGCOLOR    = \"#CCCCCC\"\n");
    printf("      TEXT       = \"#000000\">\n");
    printf("<TITLE>Fractal Worldmap Generator</TITLE>\n");
    printf("<H1>An error has ocurred</H1>\n");
    printf("<P>\n<HR>");

    if (opt)
      printf(message, opt);
    else
      printf("%s", message);

    printf("<P>\n<HR>");
    printf("</BODY>");
    printf("</HTML>");

    exit(1);
}

/*
 * Main routine, which is *too* big. I really should redesign the whole
 * program. Anybody who volounteres?
 */
int main(int argc, char **argv)
{
  char      *Args;
  int       NumberOfFaults=0, a, j, i, row, Color, MaxZ=1, MinZ=-1;
  int       index2, TwoColorMode=0, ExternalViewer=0;
  int       Threshold, Count, Cur, Generate=0, Height=-1;
  int       PercentWater, PercentIce, Mode=HEIGHT;
  unsigned  Seed = 0;


  Args = getenv("QUERY_STRING");

/*
  PrintError("<H1>I'm currently testing some things...</H1><P>QUERY_STRING=%s\n", Args);
*/

  while(Args != NULL)
  {
    for(i=0; (Args[i] != 0) && (Args[i] != '='); i++);
    
    Args[i] = 0;
    
    if (Args != NULL)
    {
      if (strcmp(Args, "Height") == 0)
      {
	Args += i+1;
	for (i=0; (Args[i] != 0) && (Args[i] != '&'); i++);
        if (i == 0) PrintError("<FONT SIZE=5>Y</FONT><FONT SIZE=3>ou didn't supply a height or a radius...</FONT>\n", NULL);
	if (sscanf(Args, "%d", &Height) == 0)
	{
	  Args[i] = 0;
	  PrintError("<FONT SIZE=5>T</FONT><FONT SIZE=3>he following string is not allowed in the seed inputfield: %s</FONT>\n", Args);
	}
	
	if (Height > 512) PrintError("<FONT SIZE=5>Y</FONT><FONT SIZE=3>ou can't specify a height over 512!!!</FONT>\n", NULL);
      }
      else if (strcmp(Args, "Generate") == 0)
      {
	Args += i+1;
	for (i=0; (Args[i] != 0) && (Args[i] != '&'); i++);
	Generate = 1;
      }
      else if (strcmp(Args, "Seed") == 0)
      {
	Args += i+1;
	for (i=0; (Args[i] != 0) && (Args[i] != '&'); i++);
        if (i == 0) PrintError("<FONT SIZE=5>Y</FONT><FONT SIZE=3>ou didn't supply a seed...\n</FONT>", NULL);
	if (sscanf(Args, "%d", &Seed) == 0)
	{
	  Args[i] = 0;
	  PrintError("<FONT SIZE=5>T</FONT><FONT SIZE=3>he following string is not allowed in the seed inputfield: %s</FONT>\n", Args);
	}
      }
      else if (strcmp(Args, "Iterations") == 0)
      {
	Args += i+1;
	for (i=0; (Args[i] != 0) && (Args[i] != '&'); i++);
        if (i == 0) PrintError("<FONT SIZE=5>Y</FONT><FONT SIZE=3>ou didn't supply the number of iterations...\n</FONT>", NULL);
	if (sscanf(Args, "%d", &NumberOfFaults) == 0)
	{
	  Args[i] = 0;
	  PrintError("<FONT SIZE=5>T</FONT><FONT SIZE=3>he following string is not allowed in the iterations inputfield: %s</FONT>\n", Args);
	}
	
	if (NumberOfFaults < 1) PrintError("<FONT SIZE=5>Y</FONT><FONT SIZE=3>ou must iterate at least 1 time!!!</FONT>\n", NULL);
	else if (NumberOfFaults > 5000) PrintError("<FONT SIZE=5>Y</FONT><FONT SIZE=3>ou can't do more than 5000 iterations!!!</FONT>\n", NULL);
      }
      else if (strcmp(Args, "PercentWater") == 0)
      {
	Args += i+1;
	for (i=0; (Args[i] != 0) && (Args[i] != '&'); i++);
        if (i == 0) PrintError("<FONT SIZE=5>Y</FONT><FONT SIZE=3>ou didn't tell me how many percent of the world should be covered with water...</FONT>\n", NULL);
	if (sscanf(Args, "%d", &PercentWater) == 0)
	{
	  Args[i] = 0;
	  PrintError("<FONT SIZE=5>T</FONT><FONT SIZE=3>he following string is not allowed in the iterations inputfield: %s</FONT>\n", Args);
	}
	
	if (PercentWater > 100)
	  PrintError("<FONT SIZE=5>Y</FONT><FONT SIZE=3>ou can't have a percentage greater then 100!!!</FONT>\n", NULL);
	else if (PercentWater < 0)
	  PrintError("<FONT SIZE=5>Y</FONT><FONT SIZE=3>ou can't have a percentage less then 0!!!</FONT>\n", NULL);
      }
      else if (strcmp(Args, "PercentIce") == 0)
      {
	Args += i+1;
	for (i=0; (Args[i] != 0) && (Args[i] != '&'); i++);
        if (i == 0) PrintError("<FONT SIZE=5>Y</FONT><FONT SIZE=3>ou didn't tell me how many percent of the world should be covered with ice-caps...</FONT>\n", NULL);
	if (sscanf(Args, "%d", &PercentIce) == 0)
	{
	  Args[i] = 0;
	  PrintError("<FONT SIZE=5>T</FONT><FONT SIZE=3>he following string is not allowed in the iterations inputfield: %s</FONT>\n", Args);
	}
	
	if (PercentIce > 100)
	  PrintError("<FONT SIZE=5>Y</FONT><FONT SIZE=3>ou can't have a percentage greater then 100!!!</FONT>\n", NULL);
	else if (PercentWater < 0)
	  PrintError("<FONT SIZE=5>Y</FONT><FONT SIZE=3>ou can't have a percentage less then 0!!!</FONT>\n", NULL);
      }
      else if (strcmp(Args, "ProjectionType") == 0)
      {
	Args += i+1;
	for (i=0; (Args[i] != 0) && (Args[i] != '&'); i++);
	for (j=0; (Args[j] != 0) && (Args[j] != '&'); j++);

	if (i == 0) PrintError("<FONT SIZE=5>Y</FONT><FONT SIZE=3>ou didn't tell me which projection to use...</FONT>\n", NULL);

	if (strncmp(Args, "Square", j) == 0)
	{
	  ProjectionType = SQUARE;
	}
	else if (strncmp(Args, "Mercator", j) == 0)
	{
	  ProjectionType = MERCATOR;
	}
	else if (strncmp(Args, "Spherical", j) == 0)
	{
	  ProjectionType = SPHERICAL;
	}
	else if (strncmp(Args, "Orthographic+NP", j) == 0)
	{
	  ProjectionType = ORTHOGRAPHIC_NP;
	}
	else if (strncmp(Args, "Orthographic+SP", j) == 0)
	{
	  ProjectionType = ORTHOGRAPHIC_SP;
	}
	else if (strncmp(Args, "Stereographic+NP", j) == 0)
	{
	  ProjectionType = STEREOGRAPHIC_NP;
	}
	else if (strncmp(Args, "Stereographic+SP", j) == 0)
	{
	  ProjectionType = STEREOGRAPHIC_SP;
	}
	else if (strncmp(Args, "Gnomic+NP", j) == 0)
	{
	  ProjectionType = GNOMIC_NP;
	}
	else if (strncmp(Args, "Gnomic+SP", j) == 0)
	{
	  ProjectionType = GNOMIC_SP;
	}
	else if (strncmp(Args, "Lambert's+areapreserving+NP", j) == 0)
	{
	  ProjectionType = LAMBERT_AREAP_NP;
	}
	else if (strncmp(Args, "Lambert's+areapreserving+SP", j) == 0)
	{
	  ProjectionType = LAMBERT_AREAP_SP;
	}
	else
	{
	  Args[i] = 0;
	  PrintError("<FONT SIZE=5>I</FONT><FONT SIZE=3> don't support the \"%s\" projection. Only:<P><UL><LI> Square\n<LI> Mercator\n<LI> Spherical\n<LI> Orthographic\n<LI> Stereographic\n<LI> Gnomic\n</UL></FONT>\n", Args);
	}
      }
      else if (strcmp(Args, "TwoColorMode") == 0)
      {
	Args += i+1;
	for (i=0; (Args[i] != 0) && (Args[i] != '&'); i++);
	TwoColorMode = 1;
      }
      else if (strcmp(Args, "ExternalViewer") == 0)
      {
	Args += i+1;
	for (i=0; (Args[i] != 0) && (Args[i] != '&'); i++);
	ExternalViewer = 1;
      }
      else if (strcmp(Args, "ScrollDegrees") == 0)
      {
	Args += i+1;
	for (i=0; (Args[i] != 0) && (Args[i] != '&'); i++);

	if (sscanf(Args, "%d", &ScrollDegrees) == 0)
	{
	  Args[i] = 0;
	  PrintError("<FONT SIZE=5>T</FONT><FONT SIZE=3>he following string is not allowed in the scroll inputfield: %s</FONT>\n", Args);
	}
      }

      if (Args[i] == 0) break;
      Args[i] = 0;
      Args += i+1;
    }
  }

  if (Height < 0) PrintError("<FONT SIZE=5>Y</FONT><FONT SIZE=3>ou MUST supply a height or a radius!!!", NULL);
  
  switch (ProjectionType)
    {
    case SQUARE:
	YRange = Height;
	XRange = 2*YRange;
	break;
    case MERCATOR:
	YRange = Height;
	XRange = (int)(((double)YRange)*PI/2);
	if (2*(XRange/2)-XRange != 0) XRange++;
	break;
    case SPHERICAL:
	YRange = (int)(((double)Height)*PI/2);
	XRange = (int)(((double)Height)*PI);
	break;
    case ORTHOGRAPHIC_NP:
    case ORTHOGRAPHIC_SP:
	YRange = (int)(((double)Height)*PI/2);
	XRange = (int)(((double)Height)*PI);
	break;
    case STEREOGRAPHIC_NP:
    case STEREOGRAPHIC_SP:
	YRange = Height;
	XRange = (int)(((double)Height)*PI);
	break;
    case GNOMIC_NP:
    case GNOMIC_SP:
	YRange = (int)(((double)Height)*PI/2);
	XRange = (int)(((double)Height)*PI);
	break;
    case LAMBERT_AREAP_NP:
    case LAMBERT_AREAP_SP:
	YRange = Height;
	XRange = (int)(((double)Height)*PI);
	break;
    default:;
    }

  if ((Generate == 0) && (ExternalViewer == 0))
  {
    printf("Content-type: text/html\n\n");
    printf("<HTML>\n\n");
    printf("<HEAD>\n<Title>Fractal Worldmap Generator</Title>\n</HEAD>\n\n");
    printf("<BODY BACKGROUND = \"http://www.lysator.liu.se/~johol/images/background.gif\">\n");
    printf("<HR>\n");
    printf("<CENTER>\n");
    printf("<IMG SRC=\"http://www.lysator.liu.se/~johol/fwmg/titles/fwmg.gif\" ALT=\"Fractal Worldmap Generator\">\n");
    printf("</CENTER>\n");
    printf("<HR> <P> <B>\n");
    
    printf("News: I have now put my source code under <a href=\"source/Copying\">GPL license</a>!\n<P>\n");

    printf("You can now generate your own worldmaps on the fly, just enter some numbers below and click submit and after a while you'll get a fractal worldmap in GIF-format!<P>\n");

    printf("One word of caution though, it might take a while to generate a map if you supply a large iterationnumber, for instance if you set the number of iterations to 15000, 640x320 bitmap, it will take about 50 seconds to generate a map... And this is when there is nearly no load on the server!<P>\n");
    printf("<EM>One can no longer generate images with a height over 512 or with more than 5000 iterations. This is because the genereator nearly crashed the WWW-server, and I don't know why the generator went bazook. :(</EM><P>\n");
    
    printf("<P><A HREF=\"http://www.lysator.liu.se/~johol/fwmg/source/worldgen.c\">Download the sourcecode for this program (V2.2, GPL license)</A>.<BR>\n");
    printf("Those who run MS/DOS can try Martijn Faassen's <A HREF=\"ftp://ftp.funet.fi/pub/doc/games/roleplay/programs/mapping/worldgen.zip\">adopted version</A> for MS/DOS!<P>\n");
    
    printf("Quite recently feywulf sent me a new port of worldgen.c which can be compiled by djgpp on DOS machines. You can either download the version sent to me by clicking <A HREF=\"http://www.lysator.liu.se/~johol/fwmg/fwmgDos.zip\">here</A>, or directly from <A HREF=\"http://matrix.crosswinds.net/~feywulf/programs.html\">feywulf's homepage</A>.<P>\n");
    
    printf("<P><A HREF=\"http://www.lysator.liu.se/~johol/fwmg/source/WorldMapGenerator.c\">Download the sourcecode for this CGI program (V1.1, GPL license)</A>.<BR><P>\n");

    printf("<A HREF=\"http://nils.jeppe.de/\">Nils Jeppe</A> have made a <A HREF=\"source/worldos2.zip\">version for OS2/Warp</A>. :)<P>\n");

    printf("<UL>\n  <LI> <A HREF=\"http://www.lysator.liu.se/~johol/fwmg/howisitdone.html\">A page for those who want to know how the fractal worldmap generator works...</A>\n");
    printf("  <LI> <A HREF=\"http://www.lysator.liu.se/~johol/fwmg/projections.html\">A page for those who want to know more about the projections...</A>\n");
    printf("</UL>\n\n<P><HR><P>\n");
    
    printf("<B><FONT SIZE=6>O</FONT>THER IMAGE GENERATING PROGRAMS FOUND ON THE NET<FONT SIZE=4></FONT></B><P>\n");
    printf("This is a (incomplete ?) list of other image generating programs that I've found or the creators have made me aware of... :)<P>\n");
    printf("<UL>\n");
    printf("  <LI> <A HREF=\"http://members.aol.com/BNHershey/home.html\">SineArt Offering From Brian N. Hershey</A>\n");
    printf("  <LI> <A HREF=\"http://www.irony.com/webdice.html\">Irony Games</A>\n");
    printf("  <LI> <A HREF=\"ftp://ftp.funet.fi/pub/doc/games/roleplay/programs/mapping/index.html\">Contents of directory programs/mapping</A>\n");
    printf("  <LI> <A HREF=\"http://www.best.com/~jendave/builder/world/index.html\">World Builder is a shareware program to draw maps of worlds. It uses continental drift and true meteorological computations to provide realistic maps including mountain ranges, rain shadows and rivers.</A>\n");
    printf("</UL><P>\n");
    printf("If you want a link to your image generator from this page, just drop me a line and I'll see what I can do! :)<P><HR><P>\n");

    printf("<Form METHOD=GET ACTION=\"http://www.lysator.liu.se/~johol/cgi-bin/worldgen.cgi\">\n");

    printf("<INPUT TYPE=INT SIZE=9 MAXLENGTH=9 NAME=Seed VALUE=\"%d\"> &#160; &#160;Random seed <P>\n", Seed);
    printf("<INPUT TYPE=INT SIZE=5 MAXLENGTH=5 NAME=Iterations VALUE=\"%d\"> &#160; &#160; Number of iterations <P>\n", NumberOfFaults);
    printf("<INPUT TYPE=INT SIZE=3 MAXLENGTH=3 NAME=PercentWater VALUE=\"%d\" RANGE MAX=100 MIN=0> &#160; &#160; Percentage of total area covered with water <P>\n", PercentWater);
    printf("<INPUT TYPE=INT SIZE=3 MAXLENGTH=3 NAME=PercentIce VALUE=\"%d\" RANGE MAX=100 MIN=0> &#160; &#160; Percentage of each hemisphere to be covered with ice <P>\n", PercentIce);
    printf("<INPUT TYPE=INT SIZE=4 MAXLENGTH=4 NAME=ScrollDegrees VALUE=\"%d\" MAX=360 MIN=-360> &#160; &#160; How many degrees to rotate the finished bitmap<P>\n", ScrollDegrees);

    printf("Which projection to use? &#160; &#160;\n<SELECT NAME=\"ProjectionType\" SIZE=5>\n");
    printf("  <OPTION"); if (ProjectionType==SQUARE) printf(" SELECTED"); printf("> Square\n");
    printf("  <OPTION"); if (ProjectionType==MERCATOR) printf(" SELECTED"); printf("> Mercator\n");
    printf("  <OPTION"); if (ProjectionType==SPHERICAL) printf(" SELECTED"); printf("> Spherical\n");
    printf("  <OPTION"); if (ProjectionType==ORTHOGRAPHIC_NP) printf(" SELECTED"); printf("> Orthographic NP\n");
    printf("  <OPTION"); if (ProjectionType==ORTHOGRAPHIC_SP) printf(" SELECTED"); printf("> Orthographic SP\n");
    printf("  <OPTION"); if (ProjectionType==STEREOGRAPHIC_NP) printf(" SELECTED"); printf("> Stereographic NP\n");
    printf("  <OPTION"); if (ProjectionType==STEREOGRAPHIC_SP) printf(" SELECTED"); printf("> Stereographic SP\n");
    printf("  <OPTION"); if (ProjectionType==GNOMIC_NP) printf(" SELECTED"); printf("> Gnomic NP\n");
    printf("  <OPTION"); if (ProjectionType==GNOMIC_SP) printf(" SELECTED"); printf("> Gnomic SP\n");
/*
    printf("  <OPTION"); if (ProjectionType==LAMBERT_AREAP_NP) printf(" SELECTED"); printf("> Lambert's areapreserving NP\n");
    printf("  <OPTION"); if (ProjectionType==LAMBERT_AREAP_SP) printf(" SELECTED"); printf("> Lambert's areapreserving SP\n");
*/
    printf("</SELECT> <P>\n");

    printf("<INPUT TYPE=INT SIZE=4 MAXLENGTH=4 NAME=Height VALUE=\"%d\" RANGE MAX=2048 MIN=100> &#160; &#160; Height of generated bitmap<P>\n", Height);

    printf("<INPUT TYPE=checkbox NAME=ExternalViewer");
    if (ExternalViewer) printf(" CHECKED"); else printf(" UNCHECKED");
    printf("> &#160; &#160; Image should not be sent in-line<P>\n");

    printf("<INPUT TYPE=checkbox NAME=TwoColorMode");
    if (TwoColorMode) printf(" CHECKED"); else printf(" UNCHECKED");
    printf("> &#160; &#160; Use two colors only<P>\n");

    printf("<INPUT TYPE=submit VALUE=Submit>\n");
    printf("</Form>\n");
    
    printf("<HR>\n<CENTER>\n");
    printf("  <IMG ALIGN=MIDDLE SRC=\"http://www.lysator.liu.se/~johol/cgi-bin/worldgen.cgi?Seed=%d&Iterations=%d&PercentWater=%d&PercentIce=%d",Seed, NumberOfFaults, PercentWater, PercentIce);
	   
    if (TwoColorMode) printf("&TwoColorMode=TwoColorMode");

    printf("&ScrollDegrees=%d",ScrollDegrees);
    printf("&ProjectionType=");

    switch (ProjectionType)
    {
    case SQUARE:
      printf("Square");
      break;
    case MERCATOR:
      printf("Mercator");
      break;
    case SPHERICAL:
      printf("Spherical");
      break;
    case ORTHOGRAPHIC_NP:
      printf("Orthographic+NP");
      break;
    case ORTHOGRAPHIC_SP:
      printf("Orthographic+SP");
      break;
    case STEREOGRAPHIC_NP:
      printf("Stereographic+NP");
      break;
    case STEREOGRAPHIC_SP:
      printf("Stereographic+SP");
      break;
    case GNOMIC_NP:
      printf("Gnomic+NP");
      break;
    case GNOMIC_SP:
      printf("Gnomic+SP");
      break;
/*
    case LAMBERT_AREAP_NP:
      printf("Lambert's+areapreserving+NP");
      break;
    case LAMBERT_AREAP_SP:
      printf("Lambert's+areapreserving+SP");
      break;
*/
    default:
      break;
    }

    printf("&Height=%d&Generate=1\" ", Height);

    switch (ProjectionType)
      {
      case SQUARE:
      case MERCATOR:
	printf("WIDTH=%d HEIGHT=%d\n", XRange, YRange);
	break;
      default:
	printf("WIDTH=%d HEIGHT=%d\n", Height, Height);
	break;
      }
    
    printf(" ALT=\"Generated image\">");
    printf("</CENTER>\n<HR>\n");

    printf("<A HREF=\"http://www.lysator.liu.se/~johol/rpg/rpg.html\">\n");
    printf("<IMG ALIGN=MIDDLE SRC=\"http://www.lysator.liu.se/~johol/icons/arrow-left.gif\" ALT=\"<--\"></A>\n");
    printf("<A HREF=\"http://www.lysator.liu.se/~johol/rpg/rpg.html\"> Back to my RPG-Page.</A>\n");
    printf("<HR>\n");
    printf("<img src=\"http://www.lysator.liu.se/~johol/images/pixelsite.gif\" align=middle> Graphics created with <A HREF=\"http://www.pixelsight.com/\">Pixelsight</A>\n");
    printf("</BODY>\n</HTML>\n");
    exit(0);
  }

  WorldMapArray = (int *) malloc(XRange*YRange*sizeof(int));
  if (WorldMapArray == NULL)
  {
    PrintError("<FONT SIZE=5>I</FONT> <FONT SIZE=3>can't allocate enough memory!!!<P> I don't think this error should occurr, but one never knows...<P>Please try again some time later...</FONT>\n", NULL);
  }

  SinIterPhi = (float *) malloc(2*XRange*sizeof(float));
  if (SinIterPhi == NULL)
  {
    PrintError("<FONT SIZE=5>I</FONT> <FONT SIZE=3>can't allocate enough memory!!!<P> I don't think this error should occurr, but one never knows...<P>Please try again some time later...</FONT>\n", NULL);
  }
  
  for (i=0; i<XRange; i++)
  {
    SinIterPhi[i] = SinIterPhi[i+XRange] = (float)sin(i*2*PI/XRange);
  }

  srand(Seed);

  for (j=0, row=0; j<XRange; j++)
  {
    WorldMapArray[row] = 0;
    for (i=1; i<YRange; i++) WorldMapArray[i+row] = INT_MIN;
    row += YRange;
  }

  /* Define some "constants" which we use frequently */
  YRangeDiv2  = YRange/2;
  YRangeDivPI = YRange/PI;

  if (ProjectionType == MERCATOR)
  {
    for (a=0; a<NumberOfFaults; a++)
    {
      GenerateMercatorWorldMap();
    }
  }
  else
  {
    for (a=0; a<NumberOfFaults; a++)
    {
      GenerateSquareWorldMap();
    }
  }
  
  /* Copy data (I have only calculated faults for 1/2 the image.
   * I can do this due to symmetry... :) */
  index2 = (XRange/2)*YRange;
  for (j=0, row=0; j<XRange/2; j++)
  {
    for (i=1; i<YRange; i++)
    {
      WorldMapArray[row+index2+YRange-i] = WorldMapArray[row+i];
    }
    row += YRange;
  }

  /* Reconstruct the real WorldMap from the WorldMapArray and FaultArray */
  for (j=0, row=0; j<XRange; j++)
  {
    /* We have to start somewhere, and the top row was initialized to 0,
     * but it might have changed during the iterations... */
    Color = WorldMapArray[row];
    for (i=1; i<YRange; i++)
    {
      Cur = WorldMapArray[row+i];
      if (Cur != INT_MIN)
      {
	Color += Cur;
      }
      WorldMapArray[row+i] = Color;
    }
    row += YRange;

  }

  /* Compute MAX and MIN values in WorldMapArray */
  for (j=0; j<XRange*YRange; j++)
  {
    Color = WorldMapArray[j];
    if (Color > MaxZ) MaxZ = Color;
    if (Color < MinZ) MinZ = Color;
  }

  /* Compute color-histogram of WorldMapArray */
  for (j=0, row=0; j<XRange; j++)
  {
    for (i=0; i<YRange; i++)
    {
      Color = (int)(((float)(WorldMapArray[row+i] - MinZ + 1) / (float)(MaxZ-MinZ+1))*30)+1;
      Histogram[Color]++;
    }
    row += YRange;
  }

  /* Threshold now holds how many pixels PercentWater means */
  Threshold = PercentWater*XRange*YRange/100;

  /* "Integrate" the histogram to decide where to put sea-level */
  for (j=0, Count=0;j<256;j++)
  {
    Count += Histogram[j];

    if (Count > Threshold) break;
  }
  
  /* Threshold now holds where sea-level is */
  Threshold = j*(MaxZ - MinZ + 1)/30 + MinZ;

  if (TwoColorMode)
  {
    for (j=0, row=0; j<XRange; j++)
    {
      for (i=0; i<YRange; i++)
      {
	Color = WorldMapArray[row+i];
	if (Color < Threshold)
	  WorldMapArray[row+i] = 3;
	else
	  WorldMapArray[row+i] = 20;
      }
      row += YRange;
    }
  }
  else
  {
    /* Scale WorldMapArray to colorrange in a way that gives you
     * a certain Ocean/Land ration */
    for (j=0, row=0; j<XRange; j++)
    {
      for (i=0; i<YRange; i++)
      {
	Color = WorldMapArray[row+i];
	
	if (Color < Threshold)
	  Color = (int)(((float)(Color - MinZ) / (float)(Threshold - MinZ))*15)+1;
	else
	  Color = (int)(((float)(Color - Threshold) / (float)(MaxZ - Threshold))*15)+16;
	
	/* Just in case... I DON't want the GIF-saver to flip out! :) */
	if (Color < 0) Color=1;
	if (Color > 255) Color=255;
	
	WorldMapArray[row+i] = Color;
      }
      row += YRange;
    }
    
    /* "Recycle" Threshold variable, and, eh, the variable still has something
     * like the same meaning... :) */
    Threshold = PercentIce*XRange*YRange/100;

    if ((Threshold <= 0) || (Threshold > XRange*YRange)) goto Finished;

    FilledPixels = 0;
    /* i==y, j==x */
    for (i=0; i<YRange; i++)
    {
      for (j=0, row=0; j<XRange; j++)
      {
	Color = WorldMapArray[row+i];
	if (Color < 32) FloodFill4(j,i,Color);
	/* FilledPixels is a global variable which FloodFill4 modifies...
         * I know it's ugly, but as it is now, this is a hack! :)
         */
	if (FilledPixels > Threshold) goto NorthPoleFinished;
        row += YRange;
      }
    }
    
NorthPoleFinished:
    FilledPixels=0;
    /* i==y, j==x */
    for (i=YRange; i>0; i--)
    {
      for (j=0, row=0; j<XRange; j++)
      {
	Color = WorldMapArray[row+i];
	if (Color < 32) FloodFill4(j,i,Color);
	/* FilledPixels is a global variable which FloodFill4 modifies...
         * I know it's ugly, but as it is now, this is a hack! :)
         */
	if (FilledPixels > Threshold) goto Finished;
        row += YRange;
      }
    }
Finished:
    FilledPixels=0;
  }


  /* Somehow, this seams to be the easy way of patching the problem of scrolling the wrong direction... ;) */
  ScrollDistance = -(int)(((float)(ScrollDegrees % 360)) * ((float)XRange)/360.0);
/*
  ScrollDistance = -ScrollDistance;
*/
  printf("Content-type: image/gif\n\n");

  /* Init ImageInfo string */
  sprintf(ImageInfo, "     Random Seed: %10u\nWater/Land ratio: %10d\n Size of ice-cap: %10d\n Scroll distance: %10d", Seed, PercentWater, PercentIce, ScrollDistance);

  /* Write GIF to stdout */
  switch (ProjectionType)
  {
  case ORTHOGRAPHIC_NP:
  case ORTHOGRAPHIC_SP:
  case STEREOGRAPHIC_NP:
  case STEREOGRAPHIC_SP:
  case GNOMIC_NP:
  case GNOMIC_SP:
  case LAMBERT_AREAP_NP:
  case LAMBERT_AREAP_SP:
  case SPHERICAL:
    /*
     * If it's a spherical projection, it will be a square map we output.
     */
    Diameter = (2*(Height/2)-Height != 0)?Height+1:Height;
    Radius   = Diameter/2;
    RSquared = Radius*Radius;
    GIFEncode(stdout, Diameter, Diameter, 1, 0, 8, Red, Green, Blue, 1, 0);
    break;
  default:
    GIFEncode(stdout, XRange, YRange, 1, 0, 8, Red, Green, Blue, 1, 0);
    break;
  }

  free(WorldMapArray);

  exit(0);
}


void FloodFill4(int x, int y, int OldColor)
{
  if (WorldMapArray[x*YRange+y] == OldColor)
  {
    if (WorldMapArray[x*YRange+y] < 16)
      WorldMapArray[x*YRange+y] = 32;
    else
      WorldMapArray[x*YRange+y] += 17;

    FilledPixels++;
    if (y-1 > 0)      FloodFill4(  x, y-1, OldColor);
    if (y+1 < YRange) FloodFill4(  x, y+1, OldColor);
    if (x-1 < 0)
      FloodFill4(XRange-1, y, OldColor);
    else
      FloodFill4(   x-1, y, OldColor);
    
    if (x+1 > XRange)
      FloodFill4(     0, y, OldColor);
    else
      FloodFill4(   x+1, y, OldColor);
  }
}

void GenerateSquareWorldMap()
{
  float         Alpha, Beta;
  float         TanB;
  float         Result, Delta;
  int           i, row, N2;
  int           Theta, Phi, Xsi;
  unsigned int  flag1;


  flag1 = rand() & 1; /*(int)((((float) rand())/MAX_RAND) + 0.5);*/
  
  /* Create a random greatcircle... */  
  Alpha = (((float) rand())/MAX_RAND-0.5)*PI; /* Rotate around x-axis */
  Beta  = (((float) rand())/MAX_RAND-0.5)*PI; /* Rotate around y-axis */

  TanB  = (float)tan(acos(cos(Alpha)*cos(Beta)));
  
  row  = 0;
  Xsi  = (int)(XRange/2-(XRange/PI)*Beta);
  
  for (Phi=0; Phi<XRange/2; Phi++)
  {
    Theta = (int)(YRangeDivPI*atan(*(SinIterPhi+Xsi-Phi+XRange)*TanB))+YRangeDiv2;
    if (flag1)
    {
      /* Rise northen hemisphere <=> lower southern */
      if (WorldMapArray[row+Theta] != INT_MIN)
	WorldMapArray[row+Theta]--;
      else
	WorldMapArray[row+Theta] = -1;
    }
    else
    {
      /* Rise southern hemisphere */
      if (WorldMapArray[row+Theta] != INT_MIN)
	WorldMapArray[row+Theta]++;
      else
	WorldMapArray[row+Theta] = 1;
    }
    row += YRange;
  }
}


void GenerateMercatorWorldMap()
{
  float         Alpha, Beta;
  float         TanB;
  float         Result, Delta;
  int           i, row, N2;
  int           Theta, Phi, Xsi;
  unsigned int  flag1;


  flag1 = rand() & 1; /*(int)((((float) rand())/INT_MAX) + 0.5);*/
  
  /* Create a random greatcircle... */  
  Alpha = (((float) rand())/MAX_RAND-0.5)*PI; /* Rotate around x-axis */
  Beta  = (((float) rand())/MAX_RAND-0.5)*PI; /* Rotate around y-axis */

  TanB  = (float)tan(acos(cos(Alpha)*cos(Beta)));
  
  row  = 0;
  Xsi  = (int)(XRange/2-(XRange/PI)*Beta);
  
  for (Phi=0; Phi<XRange/2; Phi++)
  {
    Theta  = (int)(tan(atan(*(SinIterPhi+Xsi-Phi+XRange)*TanB)/2)*YRangeDiv2)+YRangeDiv2;

    if (flag1)
    {
      /* Rise northen hemisphere <=> lower southern */
      if (WorldMapArray[row+Theta] != INT_MIN)
	WorldMapArray[row+Theta]--;
      else
	WorldMapArray[row+Theta] = -1;
    }
    else
    {
      /* Rise southern hemisphere */
      if (WorldMapArray[row+Theta] != INT_MIN)
	WorldMapArray[row+Theta]++;
      else
	WorldMapArray[row+Theta] = 1;
    }
    row += YRange;
  }
}


/*****************************************************************************
 *
 * GIFENCODE.C    - GIF Image compression interface
 *
 * GIFEncode( FName, GHeight, GWidth, GInterlace, Background,
 *            BitsPerPixel, Red, Green, Blue, Transparent, TransparentColor )
 *
 * FName             = Stream
 * GHeight           = Height
 * GWidth            = Width
 * GInterlace        = 0 if no interlace
 * Background        = Background color index
 * BitsPerPixel      = Number of bitplanes used
 * Red               = Pointer to array of red values
 * Green             = Pointer to array of green values
 * Blue              = Pointer to array of blue values
 * Transparent       = 0 if no transparant color is used
 * TransparentColor  = Transparant color index
 *
 *****************************************************************************/

#define TRUE 1
#define FALSE 0

static int Width, Height;
static int curx, cury;
static long CountDown;
static int Pass = 0;
static int Interlace;

/*
 * Bump the 'curx' and 'cury' to point to the next pixel
 */
static void
BumpPixel()
{
        /*
         * Bump the current X position
         */
        ++curx;

        /*
         * If we are at the end of a scan line, set curx back to the beginning
         * If we are interlaced, bump the cury to the appropriate spot,
         * otherwise, just increment it.
         */
        if( curx == Width ) {
                curx = 0;

                if( !Interlace )
                        ++cury;
                else {
                     switch( Pass ) {

                       case 0:
                          cury += 8;
                          if( cury >= Height ) {
                                ++Pass;
                                cury = 4;
                          }
                          break;

                       case 1:
                          cury += 8;
                          if( cury >= Height ) {
                                ++Pass;
                                cury = 2;
                          }
                          break;

                       case 2:
                          cury += 4;
                          if( cury >= Height ) {
                             ++Pass;
                             cury = 1;
                          }
                          break;

                       case 3:
                          cury += 2;
                          break;
                        }
                }
        }
}

/*
 * Return the next pixel from the image
 */
static int
GIFNextPixel( void )
{
        int     r, newx=0, newy=0, temp=0;
	double  theta, phi, spherex=0, spherez=0, b;

        if( CountDown == 0 ) return EOF;
        --CountDown;

	switch (ProjectionType)
	{
	case SPHERICAL:
	  newx = curx - Radius;
	  newy = cury - Radius;
	  temp = newx*newx + newy*newy;
	  
	  if (temp <= RSquared)
	  {
	    spherex = sqrt(((double)(RSquared - temp)));
	    newx    = (int)((atan(((double)newx)/spherex)*XRange/PI+XRange)/2)+ScrollDistance;
	    theta   = acos(((double)newy)/((double)Radius));
	    newy    = YRange-(int)(theta*YRange/PI);
	  }
	  else
	  {
	    BumpPixel();
	    return(0);
	  }
	  break;
	case ORTHOGRAPHIC_NP:
	case ORTHOGRAPHIC_SP:
	  newx = curx - Radius;
	  newx = (ProjectionType == ORTHOGRAPHIC_NP)?-newx:newx;
	  newy = cury - Radius;
	  temp = newx*newx + newy*newy;
	  
	  if (temp <= RSquared)
	  {
	    spherez = sqrt(((double)(RSquared - temp)));
	    spherez = (ProjectionType == ORTHOGRAPHIC_NP)?spherez:-spherez;

	    if (newx<0)
	      if (newy<0)
		newx  = (int)(atan(((double)newy)/((double)newx))*XRange/(2*PI))+ScrollDistance;
	      else
		newx  = (int)(atan(((double)newy)/((double)newx))*XRange/(2*PI)+XRange)+ScrollDistance;
	    else
	      newx   = (int)((atan(((double)newy)/((double)newx))*XRange/PI+XRange)/2)+ScrollDistance;
	    
	    if (ProjectionType == ORTHOGRAPHIC_NP) newx -= XRange/4;

	    newy   = (int)(2*atan(sqrt(temp)/Diameter)*YRange/PI);
	    theta  = acos(spherez/((double)Radius));
	    newy   = (int)(theta*YRange/PI);
	  }
	  else
	  {
	    BumpPixel();
	    return(0);
	  }
	  break;
	case STEREOGRAPHIC_NP:
	case STEREOGRAPHIC_SP:
	  newx = curx - Radius;
	  newx = (ProjectionType == STEREOGRAPHIC_NP)?-newx:newx;
	  newy = cury - Radius;
	  temp = newx*newx + newy*newy;
	  
	  if (temp <= RSquared)
	  {
	    if (newx<0)
	      if (newy<0)
		newx  = (int)(atan(((double)newy)/((double)newx))*XRange/(2*PI))+ScrollDistance;
	      else
		newx  = (int)(atan(((double)newy)/((double)newx))*XRange/(2*PI)+XRange)+ScrollDistance;
	    else
	      newx   = (int)((atan(((double)newy)/((double)newx))*XRange/PI+XRange)/2)+ScrollDistance;

	    if (ProjectionType == STEREOGRAPHIC_NP)
	    {
	      newx -= XRange/4;
	      newy  = (int)(2*atan(sqrt(temp)/Diameter)*YRange/PI);
	    }
	    else
	      newy  = YRange - (int)(2*atan(sqrt(temp)/Diameter)*YRange/PI);
	  }
	  else
	  {
	    BumpPixel();
	    return(0);
	  }
	  break;
	case GNOMIC_NP:
	case GNOMIC_SP:
	  newx = curx - Radius;
	  newx = (ProjectionType == GNOMIC_NP)?-newx:newx;
	  newy = cury - Radius;
	  temp = newx*newx + newy*newy;
	  
	  if (temp <= RSquared)
	  {
	    if (newx<0)
	      if (newy<0)
		newx  = (int)(atan(((double)newy)/((double)newx))*XRange/(2*PI))+ScrollDistance;
	      else
		newx  = (int)(atan(((double)newy)/((double)newx))*XRange/(2*PI)+XRange)+ScrollDistance;
	    else
	      newx   = (int)((atan(((double)newy)/((double)newx))*XRange/PI+XRange)/2)+ScrollDistance;

	    if (ProjectionType == GNOMIC_NP)
	    {
	      newx -= XRange/4;
	      newy  = (int)(atan(sqrt(temp)/Radius)*YRange/PI);
	    }
	    else
	      newy  = YRange - (int)(atan(sqrt(temp)/Radius)*YRange/PI);

	  }
	  else
	  {
	    BumpPixel();
	    return(0);
	  }
	  break;
	case LAMBERT_AREAP_NP:
	case LAMBERT_AREAP_SP:
	  newx = curx - Radius;
	  newx = (ProjectionType == LAMBERT_AREAP_NP)?-newx:newx;
	  newy = cury - Radius;
	  temp = newx*newx + newy*newy;
	  
	  if (temp <= RSquared)
	  {
	    if (newx<0)
	      if (newy<0)
		newx  = (int)(atan(((double)newy)/((double)newx))*XRange/(2*PI))+ScrollDistance;
	      else
		newx  = (int)(atan(((double)newy)/((double)newx))*XRange/(2*PI)+XRange)+ScrollDistance;
	    else
	      newx   = (int)((atan(((double)newy)/((double)newx))*XRange/PI+XRange)/2)+ScrollDistance;

	    if (ProjectionType == LAMBERT_AREAP_NP) newx -= XRange/4;

	    b    = ((double)Height)/2-sqrt(temp);
	    newy = (PI/2-asin(b/(sqrt(RSquared+b*(b-Radius*sqrt(2)))*sqrt(2))))*YRange/PI;
	  }
	  else
	  {
	    BumpPixel();
	    return(0);
	  }
	  break;
	default:
	  newy = cury;
	  newx = curx+ScrollDistance;
	  break;
	}

	if (newx < 0)
	  newx = XRange-1 - ((-newx) % XRange);
	else if (newx >= XRange)
	  newx = newx % XRange;

	/*	if ( (newx*YRange+newy) > YRange*XRange ) abort(); */
	r = WorldMapArray[ newx*YRange+newy ];

        BumpPixel();

        return r;
}

/* public */

static void
GIFEncode( fp, GWidth, GHeight, GInterlace, Background,
           BitsPerPixel, Red, Green, Blue, Transparent, TransparentColor)

FILE* fp;
int  GWidth, GHeight;
int  GInterlace;
int  Background;
int  BitsPerPixel;
int  Red[], Green[], Blue[];
char Transparent;
char TransparentColor;

{
        int B;
        int RWidth, RHeight;
        int LeftOfs, TopOfs;
        int Resolution;
        int ColorMapSize;
        int InitCodeSize;
        int i;
	int BlockLength;

        Interlace = GInterlace;

        ColorMapSize = 1 << BitsPerPixel;

        RWidth = Width = GWidth;
        RHeight = Height = GHeight;
        LeftOfs = TopOfs = 0;

        Resolution = BitsPerPixel;

        /*
         * Calculate number of bits we are expecting
         */
        CountDown = (long)Width * (long)Height;

        /*
         * Indicate which pass we are on (if interlace)
         */
        Pass = 0;

        /*
         * The initial code size
         */
        if( BitsPerPixel <= 1 )
                InitCodeSize = 2;
        else
                InitCodeSize = BitsPerPixel;

        /*
         * Set up the current x and y position
         */
        curx = cury = 0;

        /*
         * Write the Magic header
         */
        fwrite( "GIF89a", 1, 6, fp );

        /*
         * Write out the screen width and height
         */
        Putword( RWidth, fp );
        Putword( RHeight, fp );

        /*
         * Indicate that there is a global colour map
         */
        B = 0x80;       /* Yes, there is a color map */

        /*
         * OR in the resolution
         */
        B |= (Resolution - 1) << 5;

        /*
         * OR in the Bits per Pixel
         */
        B |= (BitsPerPixel - 1);

        /*
         * Write it out
         */
        fputc( B, fp );

        /*
         * Write out the Background colour
         */
        fputc( Background, fp );

        /*
         * Byte of 0's (future expansion)
         */
        fputc( 0, fp );

        /*
         * Write out the Global Colour Map
         */
        for( i=0; i<ColorMapSize; ++i ) {
                fputc( Red[i], fp );
                fputc( Green[i], fp );
                fputc( Blue[i], fp );
        }

	/*
	 * Write some info in a Comment Extension Block
	 */

	fputc( 0x21, fp ); /* Extension introducer */
	fputc( 0xFE, fp ); /* Comment Label */
	
	BlockLength = (strlen(CommentText1) > 255)?255:strlen(CommentText1);
	fputc( BlockLength, fp); /* Blocklength */
	fwrite( CommentText1, 1, BlockLength, fp ); /* Comment Data */
	
	BlockLength = (strlen(CommentText2) > 255)?255:strlen(CommentText2);
	fputc( BlockLength, fp); /* Blocklength */
	fwrite( CommentText2, 1, BlockLength, fp ); /* Comment Data */
	
	BlockLength = (strlen(CommentText3) > 255)?255:strlen(CommentText3);
	fputc( BlockLength, fp); /* Blocklength */
	fwrite( CommentText3, 1, BlockLength, fp ); /* Comment Data */
	
	BlockLength = (strlen(ImageInfo) > 255)?255:strlen(ImageInfo);
	fputc( BlockLength, fp );
	fwrite( ImageInfo, 1, BlockLength, fp);
	
	/*
	 * Write Zero-length Data Block to mark the end of the
	 * Comment Extension.
	 */
	fputc( 0x00, fp );

	if ( Transparent )
	{
	  /*
	   * Write out a Graphic Control Extension block to allow transparent
	   * color index.
	   */
        
	  /*
	   *Write an Extension Introducer
	   */
	  fputc( 0x21, fp );
	  
	  /*
	   * Write a Graphic Control Label
	   */
	  fputc( 0xF9, fp );
	  
	  /*
	   * Write Block Size
	   */
	  fputc( 0x04, fp );
	  
	  /*
	   * Write <Packed Fields> with the value of 0x01.
	   * This indicates that I have not specified any disposal metod
	   * and that user input should not be expected and that
	   * I will supply a Transparent Index later on
	   */
	  fputc( 0x01, fp );
	  
	  /*
	   * Write a zero Delay Time
	   */
	  fputc( 0x00, fp );
	  fputc( 0x00, fp );
	  
	  /*
	   * Write Transparent Color Index
	   */
	  fputc( TransparentColor, fp );
	  
	  /*
	   * Write Zero-length Data Block to mark the end of the
	   * Graphic Control Extension.
	   */
	  fputc( 0x00, fp );
	}

        /*
         * Write an Image separator
         */
        fputc( ',', fp );

        /*
         * Write the Image header
         */

        Putword( LeftOfs, fp );
        Putword( TopOfs, fp );
        Putword( Width, fp );
        Putword( Height, fp );

        /*
         * Write out whether or not the image is interlaced
         */
        if( Interlace )
                fputc( 0x40, fp );
        else
                fputc( 0x00, fp );

        /*
         * Write out the initial code size
         */
        fputc( InitCodeSize, fp );

        /*
         * Go and actually compress the data
         */
        compress( InitCodeSize+1, fp);

        /*
         * Write out a 


Zero-length packet (to end the series)
         */
        fputc( 0, fp );

        /*
         * Write the GIF file terminator
         */
        fputc( ';', fp );

        /*
         * And close the file
         */
        fclose( fp );
}

/*
 * Write out a word to the GIF file
 */
static void
Putword( w, fp )
int w;
FILE* fp;
{
        fputc( w & 0xff, fp );
        fputc( (w / 256) & 0xff, fp );
}


/***************************************************************************
 *
 *  GIFCOMPR.C       - GIF Image compression routines
 *
 *  Lempel-Ziv compression based on 'compress'.  GIF modifications by
 *  David Rowley (mgardi@watdcsu.waterloo.edu)
 *
 ***************************************************************************/

/*
 * General DEFINEs
 */

#define BITS    12

#define HSIZE  5003            /* 80% occupancy */

#ifdef NO_UCHAR
 typedef char   char_type;
#else /*NO_UCHAR*/
 typedef        unsigned char   char_type;
#endif /*NO_UCHAR*/

/*
 *
 * GIF Image compression - modified 'compress'
 *
 * Based on: compress.c - File compression ala IEEE Computer, June 1984.
 *
 * By Authors:  Spencer W. Thomas       (decvax!harpo!utah-cs!utah-gr!thomas)
 *              Jim McKie               (decvax!mcvax!jim)
 *              Steve Davies            (decvax!vax135!petsd!peora!srd)
 *              Ken Turkowski           (decvax!decwrl!turtlevax!ken)
 *              James A. Woods          (decvax!ihnp4!ames!jaw)
 *              Joe Orost               (decvax!vax135!petsd!joe)
 *
 */
#include <ctype.h>

#define ARGVAL() (*++(*argv) || (--argc && *++argv))

static int n_bits;                        /* number of bits/code */
static int maxbits = BITS;                /* user settable max # bits/code */
static code_int maxcode;                  /* maximum code, given n_bits */
static code_int maxmaxcode = (code_int)1 << BITS; /* should NEVER generate this code */
#ifdef COMPATIBLE               /* But wrong! */
# define MAXCODE(n_bits)        ((code_int) 1 << (n_bits) - 1)
#else /*COMPATIBLE*/
# define MAXCODE(n_bits)        (((code_int) 1 << (n_bits)) - 1)
#endif /*COMPATIBLE*/

static count_int htab [HSIZE];
static unsigned short codetab [HSIZE];
#define HashTabOf(i)       htab[i]
#define CodeTabOf(i)    codetab[i]

static code_int hsize = HSIZE;                 /* for dynamic table sizing */

/*
 * To save much memory, we overlay the table used by compress() with those
 * used by decompress().  The tab_prefix table is the same size and type
 * as the codetab.  The tab_suffix table needs 2**BITS characters.  We
 * get this from the beginning of htab.  The output stack uses the rest
 * of htab, and contains characters.  There is plenty of room for any
 * possible stack (stack used to be 8000 characters).
 */

#define tab_prefixof(i) CodeTabOf(i)
#define tab_suffixof(i)        ((char_type*)(htab))[i]
#define de_stack               ((char_type*)&tab_suffixof((code_int)1<<BITS))

static code_int free_ent = 0;                  /* first unused entry */

/*
 * block compression parameters -- after all codes are used up,
 * and compression rate changes, start over.
 */
static int clear_flg = 0;

static int offset;
static long int in_count = 1;            /* length of input */
static long int out_count = 0;           /* # of codes output (for debugging) */

/*
 * compress stdin to stdout
 *
 * Algorithm:  use open addressing double hashing (no chaining) on the
 * prefix code / next character combination.  We do a variant of Knuth's
 * algorithm D (vol. 3, sec. 6.4) along with G. Knott's relatively-prime
 * secondary probe.  Here, the modular division first probe is gives way
 * to a faster exclusive-or manipulation.  Also do block compression with
 * an adaptive reset, whereby the code table is cleared when the compression
 * ratio decreases, but after the table fills.  The variable-length output
 * codes are re-sized at this point, and a special CLEAR code is generated
 * for the decompressor.  Late addition:  construct the table according to
 * file size for noticeable speed improvement on small files.  Please direct
 * questions about this implementation to ames!jaw.
 */

static int g_init_bits;
static FILE* g_outfile;

static int ClearCode;
static int EOFCode;

static void
compress( init_bits, outfile)
int init_bits;
FILE* outfile;
{
    register long fcode;
    register code_int i /* = 0 */;
    register int c;
    register code_int ent;
    register code_int disp;
    register code_int hsize_reg;
    register int hshift;

    /*
     * Set up the globals:  g_init_bits - initial number of bits
     *                      g_outfile   - pointer to output file
     */
    g_init_bits = init_bits;
    g_outfile = outfile;

    /*
     * Set up the necessary values
     */
    offset = 0;
    out_count = 0;
    clear_flg = 0;
    in_count = 1;
    maxcode = MAXCODE(n_bits = g_init_bits);

    ClearCode = (1 << (init_bits - 1));
    EOFCode = ClearCode + 1;
    free_ent = ClearCode + 2;

    char_init();

    ent = GIFNextPixel( );

    hshift = 0;
    for ( fcode = (long) hsize;  fcode < 65536L; fcode *= 2L )
        ++hshift;
    hshift = 8 - hshift;                /* set hash code range bound */

    hsize_reg = hsize;
    cl_hash( (count_int) hsize_reg);            /* clear hash table */

    output( (code_int)ClearCode );

#ifdef SIGNED_COMPARE_SLOW
    while ( (c = GIFNextPixel( )) != (unsigned) EOF ) {
#else /*SIGNED_COMPARE_SLOW*/
    while ( (c = GIFNextPixel( )) != EOF ) {	/* } */
#endif /*SIGNED_COMPARE_SLOW*/

        ++in_count;

        fcode = (long) (((long) c << maxbits) + ent);
        i = (((code_int)c << hshift) ^ ent);    /* xor hashing */

        if ( HashTabOf (i) == fcode ) {
            ent = CodeTabOf (i);
            continue;
        } else if ( (long)HashTabOf (i) < 0 )      /* empty slot */
            goto nomatch;
        disp = hsize_reg - i;           /* secondary hash (after G. Knott) */
        if ( i == 0 )
            disp = 1;
probe:
        if ( (i -= disp) < 0 )
            i += hsize_reg;

        if ( HashTabOf (i) == fcode ) {
            ent = CodeTabOf (i);
            continue;
        }
        if ( (long)HashTabOf (i) > 0 )
            goto probe;
nomatch:
        output ( (code_int) ent );
        ++out_count;
        ent = c;
#ifdef SIGNED_COMPARE_SLOW
        if ( (unsigned) free_ent < (unsigned) maxmaxcode) {
#else /*SIGNED_COMPARE_SLOW*/
        if ( free_ent < maxmaxcode ) {	/* } */
#endif /*SIGNED_COMPARE_SLOW*/
            CodeTabOf (i) = free_ent++; /* code -> hashtable */
            HashTabOf (i) = fcode;
        } else
                cl_block();
    }
    /*
     * Put out the final code.
     */
    output( (code_int)ent );
    ++out_count;
    output( (code_int) EOFCode );
}

/*****************************************************************
 * TAG( output )
 *
 * Output the given code.
 * Inputs:
 *      code:   A n_bits-bit integer.  If == -1, then EOF.  This assumes
 *              that n_bits =< (long)wordsize - 1.
 * Outputs:
 *      Outputs code to the file.
 * Assumptions:
 *      Chars are 8 bits long.
 * Algorithm:
 *      Maintain a BITS character long buffer (so that 8 codes will
 * fit in it exactly).  Use the VAX insv instruction to insert each
 * code in turn.  When the buffer fills up empty it and start over.
 */

static unsigned long cur_accum = 0;
static int cur_bits = 0;

static unsigned long masks[] = { 0x0000, 0x0001, 0x0003, 0x0007, 0x000F,
                                  0x001F, 0x003F, 0x007F, 0x00FF,
                                  0x01FF, 0x03FF, 0x07FF, 0x0FFF,
                                  0x1FFF, 0x3FFF, 0x7FFF, 0xFFFF };

static void
output( code )
code_int  code;
{
    cur_accum &= masks[ cur_bits ];

    if( cur_bits > 0 )
        cur_accum |= ((long)code << cur_bits);
    else
        cur_accum = code;

    cur_bits += n_bits;

    while( cur_bits >= 8 ) {
        char_out( (unsigned int)(cur_accum & 0xff) );
        cur_accum >>= 8;
        cur_bits -= 8;
    }

    /*
     * If the next entry is going to be too big for the code size,
     * then increase it, if possible.
     */
   if ( free_ent > maxcode || clear_flg ) {

            if( clear_flg ) {

                maxcode = MAXCODE (n_bits = g_init_bits);
                clear_flg = 0;

            } else {

                ++n_bits;
                if ( n_bits == maxbits )
                    maxcode = maxmaxcode;
                else
                    maxcode = MAXCODE(n_bits);
            }
        }

    if( code == EOFCode ) {
        /*
         * At EOF, write the rest of the buffer.
         */
        while( cur_bits > 0 ) {
                char_out( (unsigned int)(cur_accum & 0xff) );
                cur_accum >>= 8;
                cur_bits -= 8;
        }

        flush_char();

        fflush( g_outfile );

        if( ferror( g_outfile ) )
                writeerr();
    }
}

/*
 * Clear out the hash table
 */
static void
cl_block ()             /* table clear for block compress */
{

        cl_hash ( (count_int) hsize );
        free_ent = ClearCode + 2;
        clear_flg = 1;

        output( (code_int)ClearCode );
}

static void
cl_hash(hsize)          /* reset code table */
register count_int hsize;
{

        register count_int *htab_p = htab+hsize;

        register long i;
        register long m1 = -1;

        i = hsize - 16;
        do {                            /* might use Sys V memset(3) here */
                *(htab_p-16) = m1;
                *(htab_p-15) = m1;
                *(htab_p-14) = m1;
                *(htab_p-13) = m1;
                *(htab_p-12) = m1;
                *(htab_p-11) = m1;
                *(htab_p-10) = m1;
                *(htab_p-9) = m1;
                *(htab_p-8) = m1;
                *(htab_p-7) = m1;
                *(htab_p-6) = m1;
                *(htab_p-5) = m1;
                *(htab_p-4) = m1;
                *(htab_p-3) = m1;
                *(htab_p-2) = m1;
                *(htab_p-1) = m1;
                htab_p -= 16;
        } while ((i -= 16) >= 0);

        for ( i += 16; i > 0; --i )
                *--htab_p = m1;
}

static void
writeerr()
{
        fprintf(stderr, "error writing output file" );
}

/******************************************************************************
 *
 * GIF Specific routines
 *
 ******************************************************************************/

/*
 * Number of characters so far in this 'packet'
 */
static int a_count;

/*
 * Set up the 'byte output' routine
 */
static void
char_init()
{
        a_count = 0;
}

/*
 * Define the storage for the packet accumulator
 */
static char accum[ 256 ];

/*
 * Add a character to the end of the current packet, and if it is 254
 * characters, flush the packet to disk.
 */
static void
char_out( c )
int c;
{
        accum[ a_count++ ] = c;
        if( a_count >= 254 )
                flush_char();
}

/*
 * Flush the packet to disk, and reset the accumulator
 */
static void
flush_char()
{
        if( a_count > 0 ) {
                fputc( a_count, g_outfile );
                fwrite( accum, 1, a_count, g_outfile );
                a_count = 0;
        }
}

/* The End */
