//Maya ASCII 2023 scene
//Name: Rock_2_9.ma
//Last modified: Mon, Aug 01, 2022 04:20:29 PM
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
fileInfo "UUID" "B6831333-4C8F-DD38-C0C6-6D8ED669AE40";
createNode transform -n "Rock_2_9";
	rename -uid "244B17C1-46B4-44D5-EB8B-04A0E5A33B95";
	setAttr ".t" -type "double3" -523.730224609375 0.96813011169433594 -360.8875732421875 ;
	setAttr ".rp" -type "double3" 523.730224609375 -0.96813011169433594 360.8875732421875 ;
	setAttr ".sp" -type "double3" 523.730224609375 -0.96813011169433594 360.8875732421875 ;
createNode mesh -n "Rock_2_9Shape" -p "Rock_2_9";
	rename -uid "2A13DEAD-4AED-ABFE-057D-B3A910691B92";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 111 ".uvst[0].uvsp[0:110]" -type "float2" 0.56379998 0.75580001
		 0.56379998 0.86390001 0.56230003 0.86390001 0.56230003 0.75580001 0.56150001 0.86390001
		 0.56169999 0.90460002 0.56220001 0.90460002 0.56220001 0.86390001 0.56239998 0.75580001
		 0.56239998 0.86390001 0.56419998 0.86390001 0.56419998 0.75580001 0.5607 0.75580001
		 0.56040001 0.75580001 0.55980003 0.75580001 0.55980003 0.86390001 0.56010002 0.86390001
		 0.56010002 0.75580001 0.56029999 0.75580001 0.56029999 0.86390001 0.56150001 0.75580001
		 0.56209999 0.86390001 0.56209999 0.75580001 0.56440002 0.86390001 0.56440002 0.75580001
		 0.56080002 0.86390001 0.56050003 0.86390001 0.56050003 0.9048 0.5607 0.9048 0.56379998
		 0.90490001 0.56330001 0.9048 0.56080002 0.90460002 0.56370002 0.9048 0.56379998 0.9048
		 0.56370002 0.85339999 0.56290001 0.85470003 0.56269997 0.85470003 0.5632 0.85339999
		 0.56040001 0.86390001 0.5607 0.86390001 0.56230003 0.9048 0.56169999 0.85339999 0.56190002
		 0.85470003 0.56220001 0.85470003 0.56220001 0.85339999 0.56029999 0.84719998 0.56220001
		 0.9048 0.56110001 0.9048 0.56099999 0.9048 0.56019998 0.75580001 0.56019998 0.84759998
		 0.56160003 0.85470003 0.56120002 0.85339999 0.56080002 0.85339999 0.5614 0.85470003
		 0.56059998 0.85339999 0.56129998 0.85470003 0.56349999 0.85339999 0.56199998 0.9429
		 0.56209999 0.94559997 0.56209999 0.94300002 0.56110001 0.94309998 0.56120002 0.94559997
		 0.56110001 0.9429 0.5614 0.94559997 0.56129998 0.94309998 0.5614 0.94309998 0.56300002
		 0.94559997 0.56309998 0.94309998 0.56080002 0.84780002 0.56339997 0.84780002 0.56349999
		 0.84780002 0.56349999 0.91689998 0.56339997 0.91689998 0.56220001 0.84780002 0.56209999
		 0.84780002 0.56209999 0.91689998 0.56220001 0.91689998 0.5607 0.84780002 0.5607 0.91689998
		 0.56080002 0.91689998 0.56169999 0.9429 0.56169999 0.94559997 0.56089997 0.94309998
		 0.56099999 0.94559997 0.56279999 0.94309998 0.56269997 0.94559997 0.56209999 0.94309998
		 0.56300002 0.94309998 0.56290001 0.94559997 0.56110001 0.91689998 0.56089997 0.91689998
		 0.56099999 0.91689998 0.56080002 0.90619999 0.56080002 0.90640002 0.56220001 0.75580001
		 0.55980003 0.75580001 0.56440002 0.75580001 0.56440002 0.86390001 0.55980003 0.86390001
		 0.56029999 0.75580001 0.56029999 0.75580001 0.56220001 0.85339999 0.56220001 0.85470003
		 0.56290001 0.85470003 0.56309998 0.94309998 0.56080002 0.84780002 0.56080002 0.84780002
		 0.56080002 0.84780002 0.56209999 0.94559997 0.56110001 0.91689998;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr -s 68 ".vt[0:67]"  511.52001953 -0.96813011 350.61572266 511.52001953 12.042198181 350.61572266
		 522.31298828 12.042198181 346.47631836 522.31298828 -0.96813011 346.47631836 528.20507813 12.042198181 373.85791016
		 526.96289063 16.9342804 370.85546875 523.17626953 16.93429565 372.29833984 522.85986328 12.042198181 375.89453125
		 521.7890625 -0.96813011 375.85107422 521.78857422 12.042198181 375.85083008 508.14892578 12.042198181 369.29956055
		 508.14892578 -0.96813011 369.29956055 534.096679688 -0.96813011 355.69287109 536.0063476563 -0.96813011 353.80981445
		 540.79931641 -0.96813011 362.11499023 540.40576172 -0.96813011 363.99804688 540.40576172 12.042198181 363.99804688
		 538.16796875 12.042198181 370.2578125 538.16796875 -0.96813011 370.25805664 537.39599609 -0.96813011 370.98217773
		 537.39501953 12.042198181 370.98242188 528.20507813 -0.96813011 373.85791016 523.93408203 12.042198181 345.88061523
		 523.93408203 -0.96813011 345.88061523 506.66113281 12.042198181 356.28076172 506.66113281 -0.96813011 356.2800293
		 507.0014648438 -0.96813011 355.27294922 507.0014648438 12.042198181 355.27270508
		 533.64648438 12.042198181 355.34057617 535.52294922 12.042198181 353.4921875 535.91113281 16.9629364 363.60083008
		 534.31982422 16.9637146 368.050537109 511.50537109 16.96786499 357.085693359 514.71142578 16.96702576 353.78051758
		 533.56835938 16.93426514 368.78881836 512.23291016 16.96138 367.49267578 511.15917969 16.96205139 358.092773438
		 512.17431641 17.43244934 357.93994141 517.58349609 17.58366394 360.1184082 519.30908203 17.58366394 358.33984375
		 515.47558594 17.4324646 354.53833008 540.79931641 12.042198181 362.11499023 536.29345703 12.042198181 354.30737305
		 534.43701172 12.042198181 356.14038086 522.10595703 16.96057129 372.2355957 526.64941406 17.43301392 370.098388672
		 525.15283203 17.58366394 366.48095703 523.089355469 17.58366394 367.26733398 522.70849609 17.4329071 371.6027832
		 536.96435547 10.030517578 352.073486328 522.63085938 16.96498108 350.74121094 530.82910156 16.96363831 357.15209961
		 531.62109375 16.96195984 357.95214844 537.096679688 -0.96813011 352.73510742 537.70166016 -0.96813011 352.91259766
		 537.70214844 10.071723938 352.9140625 536.96533203 -0.96813011 352.073974609 522.70751953 17.43264771 351.77099609
		 523.089355469 17.58366394 356.89013672 527.21679688 17.58366394 360.1184082 530.59326172 17.43289185 357.94628906
		 533.1875 17.4329071 368.056152344 528.57470703 17.58366394 365.41040039 534.81591797 17.43287659 363.50390625
		 529.42675781 17.58366394 363.02734375 513.22167969 17.43261719 367.054931641 518.12792969 17.58366394 364.88427734
		 522.859375 -0.96813011 375.89453125;
	setAttr -s 132 ".ed[0:131]"  0 1 1 1 2 0 2 3 1 3 0 0 4 5 1 5 6 1 6 7 1
		 7 4 0 8 9 1 9 10 0 10 11 0 11 8 0 12 13 1 13 14 1 14 15 0 15 12 0 15 16 1 16 17 0
		 17 18 1 18 15 0 19 20 1 20 4 0 4 21 1 21 19 0 2 22 0 22 23 0 23 3 0 10 24 0 24 25 1
		 25 11 0 26 27 1 27 1 0 0 26 0 28 29 1 29 22 0 2 28 0 16 30 0 30 31 1 31 17 1 27 32 1
		 32 33 1 33 1 1 20 34 1 34 5 1 10 35 0 35 36 1 36 24 1 37 38 1 38 39 1 39 40 1 40 37 1
		 16 41 0 41 42 0 42 43 1 43 16 0 9 44 1 44 35 1 45 46 1 46 47 1 47 48 1 48 45 1 29 49 1
		 49 22 0 2 50 0 50 51 1 51 28 1 23 13 1 12 3 0 14 41 0 43 52 1 52 30 1 13 53 1 53 54 1
		 54 14 0 54 55 1 55 41 0 23 56 0 56 53 1 49 56 1 55 42 1 57 58 1 58 59 1 59 60 1 60 57 1
		 61 62 1 62 46 1 45 61 1 63 64 1 64 62 1 61 63 1 39 58 1 57 40 1 33 50 1 65 66 1 66 38 1
		 37 65 1 59 64 1 63 60 1 47 66 1 65 48 1 59 46 1 58 47 1 66 58 1 6 48 1 48 44 1 44 6 1
		 31 61 1 61 34 1 34 31 1 60 52 1 52 51 1 51 60 1 37 32 1 32 36 1 36 37 1 56 54 0 26 25 0
		 24 27 0 8 67 0 67 7 1 7 9 0 19 18 0 17 20 0 5 45 1 30 63 1 33 40 1 57 50 1 35 65 1
		 43 28 0 42 29 0 49 55 0 67 21 0;
	setAttr -s 106 ".n[0:105]" -type "float3"  1e+20 1e+20 1e+20 1e+20 1e+20
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
		 1e+20 1e+20 1e+20 1e+20 1e+20;
	setAttr -s 65 -ch 252 ".fc[0:64]" -type "polyFaces" 
		f 4 0 1 2 3
		mu 0 4 0 1 2 3
		f 4 4 5 6 7
		mu 0 4 4 5 6 7
		f 4 8 9 10 11
		mu 0 4 8 9 10 11
		f 4 12 13 14 15
		mu 0 4 12 13 14 96
		f 4 16 17 18 19
		mu 0 4 96 15 16 17
		f 4 20 21 22 23
		mu 0 4 18 19 4 20
		f 4 24 25 26 -3
		mu 0 4 2 21 22 3
		f 4 -11 27 28 29
		mu 0 4 11 10 23 24
		f 4 30 31 -1 32
		mu 0 4 97 98 1 0
		f 4 33 34 -25 35
		mu 0 4 25 26 21 2
		f 4 36 37 38 -18
		mu 0 4 15 27 28 16
		f 4 39 40 41 -32
		mu 0 4 98 29 30 1
		f 4 42 43 -5 -22
		mu 0 4 19 31 5 4
		f 4 44 45 46 -28
		mu 0 4 10 32 33 23
		f 4 47 48 49 50
		mu 0 4 34 35 36 37
		f 4 51 52 53 54
		mu 0 4 15 99 38 39
		f 4 55 56 -45 -10
		mu 0 4 9 40 32 10
		f 4 57 58 59 60
		mu 0 4 41 42 43 44
		f 3 61 62 -35
		mu 0 3 26 45 21
		f 4 63 64 65 -36
		mu 0 4 2 46 47 25
		f 4 -27 66 -13 67
		mu 0 4 3 22 13 12
		f 4 -15 68 -52 -17
		mu 0 4 96 14 99 15
		f 4 69 70 -37 -55
		mu 0 4 39 48 27 15
		f 4 71 72 73 -14
		mu 0 4 13 100 49 14
		f 4 74 75 -69 -74
		mu 0 4 49 50 99 14
		f 4 76 77 -72 -67
		mu 0 4 22 101 100 13
		f 4 -26 -63 78 -77
		mu 0 4 22 21 45 101
		f 3 -76 79 -53
		mu 0 3 99 50 38
		f 4 80 81 82 83
		mu 0 4 102 103 51 52
		f 4 84 85 -58 86
		mu 0 4 53 54 42 41
		f 4 87 88 -85 89
		mu 0 4 55 56 54 53
		f 4 -50 90 -81 91
		mu 0 4 37 36 103 102
		f 4 -42 92 -64 -2
		mu 0 4 1 30 46 2
		f 4 93 94 -48 95
		mu 0 4 57 104 35 34
		f 4 -83 96 -88 97
		mu 0 4 52 51 56 55
		f 4 -60 98 -94 99
		mu 0 4 44 43 104 57
		f 4 -97 100 -86 -89
		mu 0 4 56 51 42 54
		f 4 -101 -82 101 -59
		mu 0 4 42 51 103 43
		f 4 -49 -95 102 -91
		mu 0 4 36 35 104 103
		f 3 -99 -102 -103
		mu 0 3 104 43 103
		f 3 103 104 105
		mu 0 3 58 59 60
		f 3 106 107 108
		mu 0 3 61 62 63
		f 3 109 110 111
		mu 0 3 64 65 66
		f 3 112 113 114
		mu 0 3 67 68 105
		f 3 -73 -78 115
		mu 0 3 69 106 107
		f 4 116 -29 117 -31
		mu 0 4 70 71 72 73
		f 4 118 119 120 -9
		mu 0 4 74 75 76 77
		f 4 121 -19 122 -21
		mu 0 4 108 78 79 80
		f 4 123 -61 -104 -6
		mu 0 4 81 82 59 58
		f 4 124 -90 -107 -38
		mu 0 4 83 84 62 61
		f 4 125 -92 126 -93
		mu 0 4 85 86 109 87
		f 4 -108 -87 -124 -44
		mu 0 4 63 62 82 81
		f 4 -110 -98 -125 -71
		mu 0 4 65 64 84 83
		f 4 -127 -84 -112 -65
		mu 0 4 87 109 64 66
		f 4 -113 -51 -126 -41
		mu 0 4 68 67 86 85
		f 4 127 -96 -115 -46
		mu 0 4 88 89 67 105
		f 4 -105 -100 -128 -57
		mu 0 4 60 59 89 88
		f 4 -111 -70 128 -66
		mu 0 4 66 65 90 110
		f 4 -106 -56 -121 -7
		mu 0 4 58 60 77 76
		f 4 -123 -39 -109 -43
		mu 0 4 80 79 61 63
		f 4 -114 -40 -118 -47
		mu 0 4 105 68 73 72
		f 4 129 -34 -129 -54
		mu 0 4 91 92 110 90
		f 4 130 -75 -116 -79
		mu 0 4 93 94 69 107
		f 4 -130 -80 -131 -62
		mu 0 4 92 91 94 93
		f 4 -23 -8 -120 131
		mu 0 4 20 4 7 95;
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
connectAttr "Rock_2_9Shape.iog" "aiStandardSurface1SG.dsm" -na;
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
// End of Rock_2_9.ma
