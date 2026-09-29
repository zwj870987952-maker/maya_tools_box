//Maya ASCII 2023 scene
//Name: Grass_1_2.ma
//Last modified: Mon, Aug 01, 2022 04:26:02 PM
//Codeset: 1252
requires maya "2023";
requires -nodeType "aiStandardSurface" "mtoa" "5.1.0";
requires "stereoCamera" "10.0";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2023";
fileInfo "version" "2023";
fileInfo "cutIdentifier" "202202161415-df43006fd3";
fileInfo "osv" "Windows 10 Home v2009 (Build: 19044)";
fileInfo "UUID" "FA4D4DEC-4E42-ECF1-7393-069DED56BF2D";
createNode transform -n "Grass_1_2";
	rename -uid "E76A3970-4093-1ACF-94B7-E086BDF2836F";
	setAttr ".t" -type "double3" -441.517333984375 0.56141996383666992 -221.5506591796875 ;
	setAttr ".rp" -type "double3" 441.517333984375 -0.56141996383666992 221.5506591796875 ;
	setAttr ".sp" -type "double3" 441.517333984375 -0.56141996383666992 221.5506591796875 ;
createNode mesh -n "Grass_1_2Shape" -p "Grass_1_2";
	rename -uid "284020A6-40E6-7E4A-5906-509FF6891C51";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 80 ".uvst[0].uvsp[0:79]" -type "float2" 0.2617 0.7931 0.2615
		 0.7931 0.26159999 0.75959998 0.26179999 0.75959998 0.26159999 0.83310002 0.26140001
		 0.833 0.26190001 0.7931 0.26199999 0.75959998 0.26179999 0.833 0.26179999 0.90249997
		 0.26179999 0.833 0.26179999 0.90249997 0.26159999 0.83310002 0.26140001 0.833 0.2617
		 0.7931 0.26190001 0.7931 0.26179999 0.75959998 0.26199999 0.75959998 0.2615 0.7931
		 0.26159999 0.75959998 0.2617 0.7931 0.26179999 0.75959998 0.26159999 0.75959998 0.2615
		 0.7931 0.26140001 0.833 0.26159999 0.83310002 0.26190001 0.7931 0.26199999 0.75959998
		 0.26179999 0.833 0.26179999 0.90249997 0.2617 0.7931 0.2615 0.7931 0.26159999 0.75959998
		 0.26179999 0.75959998 0.26159999 0.83310002 0.26140001 0.833 0.26190001 0.7931 0.26199999
		 0.75959998 0.26179999 0.833 0.26179999 0.90249997 0.2617 0.7931 0.26179999 0.75959998
		 0.26159999 0.75959998 0.2615 0.7931 0.26140001 0.833 0.26159999 0.83310002 0.26190001
		 0.7931 0.26199999 0.75959998 0.26179999 0.833 0.26179999 0.90249997 0.26179999 0.833
		 0.26159999 0.83310002 0.26179999 0.90249997 0.26140001 0.833 0.2617 0.7931 0.26190001
		 0.7931 0.26199999 0.75959998 0.26179999 0.75959998 0.2615 0.7931 0.26159999 0.75959998
		 0.2617 0.7931 0.2615 0.7931 0.26159999 0.75959998 0.26179999 0.75959998 0.26159999
		 0.83310002 0.26140001 0.833 0.26190001 0.7931 0.26199999 0.75959998 0.26179999 0.833
		 0.26179999 0.90249997 0.2617 0.7931 0.26179999 0.75959998 0.26159999 0.75959998 0.2615
		 0.7931 0.26140001 0.833 0.26159999 0.83310002 0.26190001 0.7931 0.26199999 0.75959998
		 0.26179999 0.833 0.26179999 0.90249997;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr -s 80 ".vt[0:79]"  441.20898438 1.92666054 221.41601563 441.46655273 1.58026028 220.81689453
		 441.57055664 -0.10262001 220.46179199 441.31298828 -0.10255003 221.42248535 441.33740234 2.80426025 221.59924316
		 441.57055664 2.76416969 220.98791504 441.46655273 1.58026028 222.13525391 441.57055664 -0.10262001 222.38317871
		 441.48022461 2.37647057 221.99731445 441.57055664 3.42457008 221.9173584 442.16357422 3.80123901 220.25598145
		 442.50512695 4.59405899 217.92883301 441.8918457 3.57212067 219.59558105 442.16357422 3.27747917 219.10388184
		 441.94189453 2.17321968 220.34240723 442.26855469 1.80426025 221.11853027 441.75415039 -0.55542994 220.026367188
		 442.080810547 -0.55554008 221.41174316 442.26855469 1.44137001 219.53625488 442.080810547 -0.55554008 218.64111328
		 440.8659668 2.60868073 223.81103516 440.97070313 -0.35095 223.79040527 441.50854492 -0.35107994 224.95568848
		 441.23120117 1.81488037 224.46020508 441.036376953 3.33757973 224.48742676 440.75854492 4.030281067 224.095703125
		 441.23120117 2.20849037 223.26049805 441.50854492 -0.35107994 222.9486084 441.41894531 4.37451935 223.81506348
		 440.49389648 5.44665146 225.15234375 441.63232422 3.61540985 222.95751953 442.13549805 2.9383297 222.24328613
		 442.33886719 -0.35107994 221.81994629 441.83544922 -0.35095 222.96508789 441.88305664 5.3307991 223.17590332
		 442.33886719 5.25244141 222.44714355 442.13549805 2.9383297 223.81481934 442.33886719 -0.35107994 224.11035156
		 442.16259766 4.49462128 223.65039063 442.33886719 6.54327011 223.55505371 441.24658203 1.92374992 221.41796875
		 441.35058594 -0.10140997 221.42297363 441.60571289 -0.10171998 220.4765625 441.5012207 1.57901001 220.83325195
		 441.6027832 2.75439072 221.0068359375 441.3737793 2.79463005 221.5994873 441.50170898 1.58036041 222.12011719
		 441.60595703 -0.10135001 222.36938477 441.51416016 2.37363052 221.9786377 441.60595703 3.41204071 221.9152832
		 442.19677734 3.78866959 220.24182129 441.92871094 3.56451035 219.59655762 442.54077148 4.58409882 217.93786621
		 442.19750977 3.28294945 219.12097168 441.97924805 2.17162895 220.33862305 442.3034668 1.800951 221.10302734
		 442.11621094 -0.55810022 221.39733887 441.79150391 -0.56005001 220.028198242 442.3034668 1.43869972 219.55200195
		 442.11523438 -0.56141996 218.65686035 441.20556641 2.60814095 223.82104492 441.2644043 1.81664085 224.44006348
		 441.54150391 -0.35010004 224.93505859 441.0083007813 -0.3498199 223.79321289 440.79272461 4.02835083 224.11352539
		 441.070800781 3.34383011 224.47155762 441.25952148 2.20729065 223.28869629 441.5390625 -0.35014987 222.97375488
		 441.43896484 4.36326981 223.84887695 440.52661133 5.4411087 225.17248535 441.66967773 3.6123085 222.95947266
		 441.87304688 -0.34979987 222.96582031 442.37109375 -0.35026002 221.84204102 442.16699219 2.93747902 222.26708984
		 442.36669922 5.24309921 222.47375488 441.91967773 5.3213501 223.17578125 442.16772461 2.93857956 223.79248047
		 442.37158203 -0.34991002 224.089477539 442.19213867 4.49219894 223.62390137 442.37402344 6.52983093 223.5559082;
	setAttr -s 152 ".ed[0:151]"  0 1 1 1 2 0 2 3 0 3 0 0 0 4 0 4 5 1 5 1 0
		 6 0 1 3 7 0 7 6 0 8 9 0 9 4 0 4 8 1 9 5 0 6 8 0 10 11 0 11 12 0 12 10 0 11 13 0 13 12 1
		 14 15 1 15 10 0 12 14 0 14 16 0 16 17 0 17 15 0 18 14 1 13 18 0 18 19 0 19 16 0 20 21 0
		 21 22 0 22 23 0 23 20 1 23 24 0 24 25 1 25 20 0 26 27 0 27 21 0 20 26 1 25 28 1 28 26 0
		 24 29 0 29 25 0 29 28 0 30 31 1 31 32 0 32 33 0 33 30 0 30 34 0 34 35 1 35 31 0 36 30 1
		 33 37 0 37 36 0 38 39 0 39 34 0 34 38 1 39 35 0 36 38 0 40 41 0 41 42 0 42 43 0 43 40 1
		 43 44 0 44 45 1 45 40 0 46 47 0 47 41 0 40 46 1 48 45 1 45 49 0 49 48 0 44 49 0 48 46 0
		 50 51 0 51 52 0 52 50 0 51 53 1 53 52 0 54 51 0 50 55 0 55 54 1 55 56 0 56 57 0 57 54 0
		 58 53 0 54 58 1 57 59 0 59 58 0 60 61 1 61 62 0 62 63 0 63 60 0 60 64 0 64 65 1 65 61 0
		 66 60 1 63 67 0 67 66 0 66 68 0 68 64 1 64 69 0 69 65 0 68 69 0 70 71 0 71 72 0 72 73 0
		 73 70 1 73 74 0 74 75 1 75 70 0 76 77 0 77 71 0 70 76 1 78 75 1 75 79 0 79 78 0 74 79 0
		 78 76 0 7 47 0 46 6 1 2 42 0 41 3 1 1 43 1 8 48 1 49 9 0 44 5 0 16 57 1 56 17 0 10 50 0
		 52 11 0 53 13 0 58 18 0 15 55 1 59 19 0 21 63 1 62 22 0 26 66 1 67 27 0 61 23 1 28 68 0
		 65 24 0 69 29 0 37 77 0 76 36 1 32 72 0 71 33 1 31 73 1 38 78 1 79 39 0 74 35 0;
	setAttr -s 218 ".n";
	setAttr ".n[0:165]" -type "float3"  1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20;
	setAttr ".n[166:217]" -type "float3"  1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20;
	setAttr -s 80 -ch 304 ".fc[0:79]" -type "polyFaces" 
		f 4 0 1 2 3
		mu 0 4 0 1 2 3
		f 4 -1 4 5 6
		mu 0 4 1 0 4 5
		f 4 7 -4 8 9
		mu 0 4 6 0 3 7
		f 3 10 11 12
		mu 0 3 8 9 4
		f 3 -12 13 -6
		mu 0 3 4 9 5
		f 4 -8 14 -13 -5
		mu 0 4 0 6 8 4
		f 3 15 16 17
		mu 0 3 10 11 12
		f 3 -17 18 19
		mu 0 3 12 11 13
		f 4 20 21 -18 22
		mu 0 4 14 15 10 12
		f 4 -21 23 24 25
		mu 0 4 15 14 16 17
		f 4 26 -23 -20 27
		mu 0 4 18 14 12 13
		f 4 -27 28 29 -24
		mu 0 4 14 18 19 16
		f 4 30 31 32 33
		mu 0 4 20 21 22 23
		f 4 34 35 36 -34
		mu 0 4 23 24 25 20
		f 4 37 38 -31 39
		mu 0 4 26 27 21 20
		f 4 -37 40 41 -40
		mu 0 4 20 25 28 26
		f 3 -36 42 43
		mu 0 3 25 24 29
		f 3 -41 -44 44
		mu 0 3 28 25 29
		f 4 45 46 47 48
		mu 0 4 30 31 32 33
		f 4 -46 49 50 51
		mu 0 4 31 30 34 35
		f 4 52 -49 53 54
		mu 0 4 36 30 33 37
		f 3 55 56 57
		mu 0 3 38 39 34
		f 3 -57 58 -51
		mu 0 3 34 39 35
		f 4 -53 59 -58 -50
		mu 0 4 30 36 38 34
		f 4 60 61 62 63
		mu 0 4 40 41 42 43
		f 4 64 65 66 -64
		mu 0 4 43 44 45 40
		f 4 67 68 -61 69
		mu 0 4 46 47 41 40
		f 3 70 71 72
		mu 0 3 48 45 49
		f 3 -66 73 -72
		mu 0 3 45 44 49
		f 4 -67 -71 74 -70
		mu 0 4 40 45 48 46
		f 3 75 76 77
		mu 0 3 50 51 52
		f 3 78 79 -77
		mu 0 3 51 53 52
		f 4 80 -76 81 82
		mu 0 4 54 51 50 55
		f 4 83 84 85 -83
		mu 0 4 55 56 57 54
		f 4 86 -79 -81 87
		mu 0 4 58 53 51 54
		f 4 -86 88 89 -88
		mu 0 4 54 57 59 58
		f 4 90 91 92 93
		mu 0 4 60 61 62 63
		f 4 -91 94 95 96
		mu 0 4 61 60 64 65
		f 4 97 -94 98 99
		mu 0 4 66 60 63 67
		f 4 -98 100 101 -95
		mu 0 4 60 66 68 64
		f 3 102 103 -96
		mu 0 3 64 69 65
		f 3 104 -103 -102
		mu 0 3 68 69 64
		f 4 105 106 107 108
		mu 0 4 70 71 72 73
		f 4 109 110 111 -109
		mu 0 4 73 74 75 70
		f 4 112 113 -106 114
		mu 0 4 76 77 71 70
		f 3 115 116 117
		mu 0 3 78 75 79
		f 3 -111 118 -117
		mu 0 3 75 74 79
		f 4 -112 -116 119 -115
		mu 0 4 70 75 78 76
		f 4 -10 120 -68 121
		mu 0 4 6 7 47 46
		f 4 -3 122 -62 123
		mu 0 4 3 2 42 41
		f 4 -2 124 -63 -123
		mu 0 4 2 1 43 42
		f 4 -9 -124 -69 -121
		mu 0 4 7 3 41 47
		f 4 -11 125 -73 126
		mu 0 4 9 8 48 49
		f 4 -14 -127 -74 127
		mu 0 4 5 9 49 44
		f 4 -7 -128 -65 -125
		mu 0 4 1 5 44 43
		f 4 -15 -122 -75 -126
		mu 0 4 8 6 46 48
		f 4 -25 128 -85 129
		mu 0 4 17 16 57 56
		f 4 -16 130 -78 131
		mu 0 4 11 10 50 52
		f 4 -19 -132 -80 132
		mu 0 4 13 11 52 53
		f 4 -28 -133 -87 133
		mu 0 4 18 13 53 58
		f 4 -22 134 -82 -131
		mu 0 4 10 15 55 50
		f 4 -29 -134 -90 135
		mu 0 4 19 18 58 59
		f 4 -26 -130 -84 -135
		mu 0 4 15 17 56 55
		f 4 -30 -136 -89 -129
		mu 0 4 16 19 59 57
		f 4 -32 136 -93 137
		mu 0 4 22 21 63 62
		f 4 -38 138 -100 139
		mu 0 4 27 26 66 67
		f 4 -33 -138 -92 140
		mu 0 4 23 22 62 61
		f 4 -42 141 -101 -139
		mu 0 4 26 28 68 66
		f 4 -35 -141 -97 142
		mu 0 4 24 23 61 65
		f 4 -43 -143 -104 143
		mu 0 4 29 24 65 69
		f 4 -45 -144 -105 -142
		mu 0 4 28 29 69 68
		f 4 -39 -140 -99 -137
		mu 0 4 21 27 67 63
		f 4 -55 144 -113 145
		mu 0 4 36 37 77 76
		f 4 -48 146 -107 147
		mu 0 4 33 32 72 71
		f 4 -47 148 -108 -147
		mu 0 4 32 31 73 72
		f 4 -54 -148 -114 -145
		mu 0 4 37 33 71 77
		f 4 -56 149 -118 150
		mu 0 4 39 38 78 79
		f 4 -59 -151 -119 151
		mu 0 4 35 39 79 74
		f 4 -52 -152 -110 -149
		mu 0 4 31 35 74 73
		f 4 -60 -146 -120 -150
		mu 0 4 38 36 76 78;
	setAttr ".cd" -type "dataPolyComponent" Index_Data Edge 0 ;
	setAttr ".cvd" -type "dataPolyComponent" Index_Data Vertex 0 ;
	setAttr ".pd[0]" -type "dataPolyComponent" Index_Data UV 0 ;
	setAttr ".hfd" -type "dataPolyComponent" Index_Data Face 0 ;
	setAttr ".db" yes;
	setAttr ".de" 1;
	setAttr ".bw" 5;
createNode materialInfo -n "materialInfo1";
	rename -uid "2525C32B-4C69-91A2-4C1D-41BDFC460F88";
createNode shadingEngine -n "aiStandardSurface1SG";
	rename -uid "8472593A-4BE3-7326-2990-7BB44705F98A";
	setAttr ".ihi" 0;
	setAttr -s 355 ".dsm";
	setAttr ".ro" yes;
createNode aiStandardSurface -n "Toon_shd";
	rename -uid "466C0731-4F60-BED2-D82C-D28AF0D43EBA";
	setAttr ".base" 0;
	setAttr ".subsurface" 1;
	setAttr ".subsurface_scale" 0.5;
	setAttr ".subsurface_type" 2;
	setAttr ".sheen_color" -type "float3" 0.22946176 0.22946176 0.22946176 ;
	setAttr ".sheen_roughness" 0.27762040495872498;
	setAttr ".coat_roughness" 0.26865673065185547;
	setAttr ".coat_IOR" 1.5315315723419189;
	setAttr ".emission" 1;
	setAttr ".emission_color" -type "float3" 0 0 0 ;
createNode file -n "file1";
	rename -uid "3486876B-4D3F-23F8-57CB-FDABC798AFE8";
	setAttr ".ftn" -type "string" "C:/Users/chauliac/Dropbox/WZX/Works In Progress/AssetIt/00_Ressources/RESSOURCES/Medieval Toon/textures/Gradient-F.png";
	setAttr ".cs" -type "string" "Raw";
createNode place2dTexture -n "place2dTexture1";
	rename -uid "78B6D35C-41B7-6D51-D8E0-07964DD1A7A1";
createNode lightLinker -s -n "lightLinker1";
	rename -uid "2940B33D-4B53-4605-2C66-069D7C9025F8";
	setAttr -s 4 ".lnk";
	setAttr -s 4 ".slnk";
select -ne :time1;
	setAttr ".o" 0;
select -ne :hardwareRenderingGlobals;
	setAttr ".otfna" -type "stringArray" 22 "NURBS Curves" "NURBS Surfaces" "Polygons" "Subdiv Surface" "Particles" "Particle Instance" "Fluids" "Strokes" "Image Planes" "UI" "Lights" "Cameras" "Locators" "Joints" "IK Handles" "Deformers" "Motion Trails" "Components" "Hair Systems" "Follicles" "Misc. UI" "Ornaments"  ;
	setAttr ".otfva" -type "Int32Array" 22 0 1 1 1 1 1
		 1 1 1 0 0 0 0 0 0 0 0 0
		 0 0 0 0 ;
	setAttr ".mhl" 10;
	setAttr ".hwi" yes;
	setAttr ".msaa" yes;
	setAttr ".aasc" 4;
	setAttr ".laa" yes;
	setAttr ".fprt" yes;
select -ne :renderPartition;
	setAttr -s 4 ".st";
select -ne :renderGlobalsList1;
select -ne :defaultShaderList1;
	setAttr -s 9 ".s";
select -ne :postProcessList1;
	setAttr -s 2 ".p";
select -ne :defaultRenderUtilityList1;
	setAttr -s 4 ".u";
select -ne :defaultRenderingList1;
select -ne :lightList1;
	setAttr -s 3 ".l";
select -ne :defaultTextureList1;
	setAttr -s 4 ".tx";
select -ne :lambert1;
	setAttr ".c" -type "float3" 0.40509915 0.40509915 0.40509915 ;
select -ne :standardSurface1;
	setAttr ".b" 0.80000001192092896;
	setAttr ".bc" -type "float3" 1 1 1 ;
	setAttr ".s" 0.20000000298023224;
select -ne :initialShadingGroup;
	setAttr ".ro" yes;
select -ne :initialParticleSE;
	setAttr ".ro" yes;
select -ne :defaultRenderGlobals;
	addAttr -ci true -h true -sn "dss" -ln "defaultSurfaceShader" -dt "string";
	setAttr ".ren" -type "string" "arnold";
	setAttr ".outf" 51;
	setAttr ".imfkey" -type "string" "exr";
	setAttr ".ifp" -type "string" "None";
	setAttr ".dss" -type "string" "lambert1";
select -ne :defaultResolution;
	setAttr ".w" 2048;
	setAttr ".h" 2048;
	setAttr ".pa" 1;
	setAttr ".dar" 1;
select -ne :defaultLightSet;
	setAttr -s 3 ".dsm";
select -ne :defaultColorMgtGlobals;
	setAttr ".cfe" yes;
	setAttr ".cfp" -type "string" "<MAYA_RESOURCES>/OCIO-configs/Maya2022-default/config.ocio";
	setAttr ".vtn" -type "string" "ACES 1.0 SDR-video (sRGB)";
	setAttr ".vn" -type "string" "ACES 1.0 SDR-video";
	setAttr ".dn" -type "string" "sRGB";
	setAttr ".wsn" -type "string" "ACEScg";
	setAttr ".otn" -type "string" "ACES 1.0 SDR-video (sRGB)";
	setAttr ".potn" -type "string" "ACES 1.0 SDR-video (sRGB)";
select -ne :hardwareRenderGlobals;
	setAttr ".ctrs" 256;
	setAttr ".btrs" 512;
connectAttr "aiStandardSurface1SG.msg" "materialInfo1.sg";
connectAttr "Toon_shd.msg" "materialInfo1.m";
connectAttr "Toon_shd.msg" "materialInfo1.t" -na;
connectAttr "Toon_shd.out" "aiStandardSurface1SG.ss";
connectAttr "Grass_1_2Shape.iog" "aiStandardSurface1SG.dsm" -na;
connectAttr "file1.oc" "Toon_shd.base_color";
connectAttr "file1.oc" "Toon_shd.subsurface_color";
connectAttr ":defaultColorMgtGlobals.cme" "file1.cme";
connectAttr ":defaultColorMgtGlobals.cfe" "file1.cmcf";
connectAttr ":defaultColorMgtGlobals.cfp" "file1.cmcp";
connectAttr ":defaultColorMgtGlobals.wsn" "file1.ws";
connectAttr "place2dTexture1.c" "file1.c";
connectAttr "place2dTexture1.tf" "file1.tf";
connectAttr "place2dTexture1.rf" "file1.rf";
connectAttr "place2dTexture1.mu" "file1.mu";
connectAttr "place2dTexture1.mv" "file1.mv";
connectAttr "place2dTexture1.s" "file1.s";
connectAttr "place2dTexture1.wu" "file1.wu";
connectAttr "place2dTexture1.wv" "file1.wv";
connectAttr "place2dTexture1.re" "file1.re";
connectAttr "place2dTexture1.of" "file1.of";
connectAttr "place2dTexture1.r" "file1.ro";
connectAttr "place2dTexture1.n" "file1.n";
connectAttr "place2dTexture1.vt1" "file1.vt1";
connectAttr "place2dTexture1.vt2" "file1.vt2";
connectAttr "place2dTexture1.vt3" "file1.vt3";
connectAttr "place2dTexture1.vc1" "file1.vc1";
connectAttr "place2dTexture1.o" "file1.uv";
connectAttr "place2dTexture1.ofs" "file1.fs";
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" "aiStandardSurface1SG.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" "aiStandardSurface1SG.message" ":defaultLightSet.message";
connectAttr "aiStandardSurface1SG.pa" ":renderPartition.st" -na;
connectAttr "Toon_shd.msg" ":defaultShaderList1.s" -na;
connectAttr "place2dTexture1.msg" ":defaultRenderUtilityList1.u" -na;
connectAttr "file1.msg" ":defaultTextureList1.tx" -na;
// End of Grass_1_2.ma
