//Maya ASCII 2023 scene
//Name: Grass_1_4.ma
//Last modified: Mon, Aug 01, 2022 04:26:20 PM
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
fileInfo "UUID" "46C177A5-4001-B3B5-31D7-C9B9B234C4FF";
createNode transform -n "Grass_1_4";
	rename -uid "338CEBF4-48A1-2CE3-7492-76B5CD77C66F";
	setAttr ".t" -type "double3" -447.2769775390625 0.10262001305818558 -227.593017578125 ;
	setAttr ".rp" -type "double3" 447.2769775390625 -0.10262001305818558 227.593017578125 ;
	setAttr ".sp" -type "double3" 447.2769775390625 -0.10262001305818558 227.593017578125 ;
createNode mesh -n "Grass_1_4Shape" -p "Grass_1_4";
	rename -uid "A8D5E86A-4E5C-EC8A-BDB0-569A8574967C";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 60 ".uvst[0].uvsp[0:59]" -type "float2" 0.2617 0.7931 0.26179999
		 0.75959998 0.26159999 0.75959998 0.2615 0.7931 0.26140001 0.833 0.26159999 0.83310002
		 0.26190001 0.7931 0.26199999 0.75959998 0.26179999 0.833 0.26179999 0.90249997 0.2617
		 0.7931 0.2615 0.7931 0.26159999 0.75959998 0.26179999 0.75959998 0.26159999 0.83310002
		 0.26140001 0.833 0.26190001 0.7931 0.26199999 0.75959998 0.26179999 0.833 0.26179999
		 0.90249997 0.2617 0.7931 0.2615 0.7931 0.26159999 0.75959998 0.26179999 0.75959998
		 0.26159999 0.83310002 0.26140001 0.833 0.26190001 0.7931 0.26199999 0.75959998 0.26179999
		 0.833 0.26179999 0.90249997 0.2617 0.7931 0.2615 0.7931 0.26159999 0.75959998 0.26179999
		 0.75959998 0.26159999 0.83310002 0.26140001 0.833 0.26190001 0.7931 0.26199999 0.75959998
		 0.26179999 0.833 0.26179999 0.90249997 0.2617 0.7931 0.26179999 0.75959998 0.26159999
		 0.75959998 0.2615 0.7931 0.26140001 0.833 0.26159999 0.83310002 0.26190001 0.7931
		 0.26199999 0.75959998 0.26179999 0.833 0.26179999 0.90249997 0.2617 0.7931 0.26179999
		 0.75959998 0.26159999 0.75959998 0.2615 0.7931 0.26140001 0.833 0.26159999 0.83310002
		 0.26190001 0.7931 0.26199999 0.75959998 0.26179999 0.833 0.26179999 0.90249997;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr -s 60 ".vt[0:59]"  446.89013672 1.41160965 226.7532959 446.94384766 -0.10255003 226.73596191
		 447.21899414 -0.10262001 227.71362305 447.077148438 1.0054998398 227.29785156 446.97729492 1.7845192 227.32067871
		 446.83520508 2.13891029 226.9921875 447.077148438 1.20687008 226.29150391 447.21899414 -0.10262001 226.029785156
		 447.1730957 2.31502914 226.75671387 446.69970703 2.86354065 227.87841797 447.18383789 0.76154995 228.54833984
		 447.36865234 0.68660975 228.16333008 447.36865234 -0.085070014 227.90283203 447.18383789 -0.085030019 228.50048828
		 447.30786133 1.5431509 228.81054688 447.49267578 1.41829014 228.48046875 447.36865234 0.68660975 228.92773438
		 447.36865234 -0.085070014 229.098144531 447.49267578 1.41829014 228.98095703 447.27075195 2.28083992 229.15625
		 447.53833008 0.71555996 227.65112305 447.70800781 0.64669991 227.24780273 447.70800781 -0.062290013 227.13635254
		 447.53833008 -0.062259972 227.68530273 447.625 1.43367004 227.83984375 447.82202148 1.3189497 227.60302734
		 447.70800781 0.64669991 228.047607422 447.70800781 -0.062290013 228.23461914 447.82202148 1.3189497 228.19091797
		 447.61816406 2.11142921 227.58227539 446.92700195 1.41028976 226.76171875 447.11279297 1.0076303482 227.28479004
		 447.25463867 -0.10156 227.69995117 446.98144531 -0.10141999 226.73803711 446.87060547 2.13401985 227.0061035156
		 447.013427734 1.79157066 227.3112793 447.11010742 1.20512009 226.31201172 447.25341797 -0.10156 226.047119141
		 447.19921875 2.30139923 226.7833252 446.73583984 2.85965919 227.88964844 447.22094727 0.75610018 228.54956055
		 447.22143555 -0.086970031 228.50097656 447.40307617 -0.087570012 227.91992188 447.40161133 0.68065023 228.18310547
		 447.52197266 1.40744019 228.50463867 447.34545898 1.54106045 228.80981445 447.40136719 0.68576002 228.90649414
		 447.40332031 -0.086059988 229.081054688 447.52197266 1.42185974 228.95410156 447.30810547 2.28380013 229.15307617
		 447.57543945 0.71054983 227.65429688 447.57592773 -0.063639998 227.68481445 447.74291992 -0.062940001 227.15246582
		 447.74121094 0.64189005 227.26757813 447.85131836 1.313591 227.62939453 447.66235352 1.43066025 227.83740234
		 447.74194336 0.64529991 228.029052734 447.74291992 -0.064170003 228.21826172 447.85424805 1.31634045 228.16870117
		 447.65576172 2.11268044 227.58520508;
	setAttr -s 114 ".ed[0:113]"  0 1 0 1 2 0 2 3 0 3 0 1 3 4 0 4 5 1 5 0 0
		 6 7 0 7 1 0 0 6 1 5 8 1 8 6 0 4 9 0 9 5 0 9 8 0 10 11 1 11 12 0 12 13 0 13 10 0 10 14 0
		 14 15 1 15 11 0 16 10 1 13 17 0 17 16 0 18 19 0 19 14 0 14 18 1 19 15 0 16 18 0 20 21 1
		 21 22 0 22 23 0 23 20 0 20 24 0 24 25 0 25 21 0 26 20 1 23 27 0 27 26 0 28 29 0 29 24 0
		 24 28 1 29 25 0 26 28 0 30 31 1 31 32 0 32 33 0 33 30 0 30 34 0 34 35 1 35 31 0 36 30 1
		 33 37 0 37 36 0 36 38 0 38 34 1 34 39 0 39 35 0 38 39 0 40 41 0 41 42 0 42 43 0 43 40 1
		 43 44 0 44 45 1 45 40 0 46 47 0 47 41 0 40 46 1 48 45 1 45 49 0 49 48 0 44 49 0 48 46 0
		 50 51 0 51 52 0 52 53 0 53 50 1 53 54 0 54 55 0 55 50 0 56 57 0 57 51 0 50 56 1 58 55 1
		 55 59 0 59 58 0 54 59 0 58 56 0 1 33 1 32 2 0 6 36 1 37 7 0 31 3 1 8 38 0 35 4 0
		 39 9 0 17 47 0 46 16 1 12 42 0 41 13 1 11 43 1 18 48 1 49 19 0 44 15 1 27 57 0 56 26 1
		 22 52 0 51 23 1 21 53 1 28 58 0 59 29 0 54 25 1;
	setAttr -s 160 ".n[0:159]" -type "float3"  1e+20 1e+20 1e+20 1e+20 1e+20
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
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20;
	setAttr -s 60 -ch 228 ".fc[0:59]" -type "polyFaces" 
		f 4 0 1 2 3
		mu 0 4 0 1 2 3
		f 4 4 5 6 -4
		mu 0 4 3 4 5 0
		f 4 7 8 -1 9
		mu 0 4 6 7 1 0
		f 4 -7 10 11 -10
		mu 0 4 0 5 8 6
		f 3 -6 12 13
		mu 0 3 5 4 9
		f 3 -11 -14 14
		mu 0 3 8 5 9
		f 4 15 16 17 18
		mu 0 4 10 11 12 13
		f 4 -16 19 20 21
		mu 0 4 11 10 14 15
		f 4 22 -19 23 24
		mu 0 4 16 10 13 17
		f 3 25 26 27
		mu 0 3 18 19 14
		f 3 -27 28 -21
		mu 0 3 14 19 15
		f 4 -23 29 -28 -20
		mu 0 4 10 16 18 14
		f 4 30 31 32 33
		mu 0 4 20 21 22 23
		f 4 -31 34 35 36
		mu 0 4 21 20 24 25
		f 4 37 -34 38 39
		mu 0 4 26 20 23 27
		f 3 40 41 42
		mu 0 3 28 29 24
		f 3 -42 43 -36
		mu 0 3 24 29 25
		f 4 -38 44 -43 -35
		mu 0 4 20 26 28 24
		f 4 45 46 47 48
		mu 0 4 30 31 32 33
		f 4 -46 49 50 51
		mu 0 4 31 30 34 35
		f 4 52 -49 53 54
		mu 0 4 36 30 33 37
		f 4 -53 55 56 -50
		mu 0 4 30 36 38 34
		f 3 57 58 -51
		mu 0 3 34 39 35
		f 3 59 -58 -57
		mu 0 3 38 39 34
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
		f 4 75 76 77 78
		mu 0 4 50 51 52 53
		f 4 79 80 81 -79
		mu 0 4 53 54 55 50
		f 4 82 83 -76 84
		mu 0 4 56 57 51 50
		f 3 85 86 87
		mu 0 3 58 55 59
		f 3 -81 88 -87
		mu 0 3 55 54 59
		f 4 -82 -86 89 -85
		mu 0 4 50 55 58 56
		f 4 -2 90 -48 91
		mu 0 4 2 1 33 32
		f 4 -8 92 -55 93
		mu 0 4 7 6 36 37
		f 4 -3 -92 -47 94
		mu 0 4 3 2 32 31
		f 4 -12 95 -56 -93
		mu 0 4 6 8 38 36
		f 4 -5 -95 -52 96
		mu 0 4 4 3 31 35
		f 4 -13 -97 -59 97
		mu 0 4 9 4 35 39
		f 4 -15 -98 -60 -96
		mu 0 4 8 9 39 38
		f 4 -9 -94 -54 -91
		mu 0 4 1 7 37 33
		f 4 -25 98 -68 99
		mu 0 4 16 17 47 46
		f 4 -18 100 -62 101
		mu 0 4 13 12 42 41
		f 4 -17 102 -63 -101
		mu 0 4 12 11 43 42
		f 4 -24 -102 -69 -99
		mu 0 4 17 13 41 47
		f 4 -26 103 -73 104
		mu 0 4 19 18 48 49
		f 4 -29 -105 -74 105
		mu 0 4 15 19 49 44
		f 4 -22 -106 -65 -103
		mu 0 4 11 15 44 43
		f 4 -30 -100 -75 -104
		mu 0 4 18 16 46 48
		f 4 -40 106 -83 107
		mu 0 4 26 27 57 56
		f 4 -33 108 -77 109
		mu 0 4 23 22 52 51
		f 4 -32 110 -78 -109
		mu 0 4 22 21 53 52
		f 4 -39 -110 -84 -107
		mu 0 4 27 23 51 57
		f 4 -41 111 -88 112
		mu 0 4 29 28 58 59
		f 4 -44 -113 -89 113
		mu 0 4 25 29 59 54
		f 4 -37 -114 -80 -111
		mu 0 4 21 25 54 53
		f 4 -45 -108 -90 -112
		mu 0 4 28 26 56 58;
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
connectAttr "Grass_1_4Shape.iog" "aiStandardSurface1SG.dsm" -na;
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
// End of Grass_1_4.ma
