//Maya ASCII 2023 scene
//Name: Spike_1.ma
//Last modified: Fri, Aug 05, 2022 06:42:19 PM
//Codeset: 1252
requires maya "2023";
requires -nodeType "aiStandardSurface" "mtoa" "5.1.0";
requires "stereoCamera" "10.0";
requires "stereoCamera" "10.0";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2023";
fileInfo "version" "2023";
fileInfo "cutIdentifier" "202202161415-df43006fd3";
fileInfo "osv" "Windows 10 Home v2009 (Build: 19044)";
fileInfo "UUID" "0C09E2E0-4935-7A57-2C68-189E106D89C4";
createNode transform -n "Spike_1";
	rename -uid "A09B7AD9-4CD2-90E5-79F6-8AA4EC19E282";
	setAttr ".t" -type "double3" 505.640869140625 -6.2843513488769531 -431.0675048828125 ;
	setAttr ".rp" -type "double3" -505.640869140625 6.2843513488769531 431.0675048828125 ;
	setAttr ".sp" -type "double3" -505.640869140625 6.2843513488769531 431.0675048828125 ;
createNode mesh -n "Spike_1Shape" -p "Spike_1";
	rename -uid "91E23017-4C68-57AA-C599-26BB71A6DC97";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 79 ".uvst[0].uvsp[0:78]" -type "float2" 0.84549999 0.18979999
		 0.84490001 0.19230001 0.8452 0.19329999 0.84500003 0.080700003 0.84549999 0.076499999
		 0.84439999 0.076899998 0.84549999 0.080700003 0.84600002 0.18979999 0.84560001 0.1943
		 0.84600002 0.080700003 0.84649998 0.076899998 0.84500003 0.18979999 0.84380001 0.19580001
		 0.84420002 0.19660001 0.84460002 0.19750001 0.84299999 0.1991 0.84350002 0.1996 0.84399998
		 0.2001 0.84350002 0.20379999 0.84310001 0.2043 0.84399998 0.2032 0.84439999 0.2071
		 0.84460002 0.2058 0.8448 0.20460001 0.85100001 0.2071 0.85089999 0.2058 0.85089999
		 0.2044 0.85290003 0.20379999 0.84399998 0.073600002 0.84399998 0.0691 0.84439999
		 0.064999998 0.84549999 0.064099997 0.84649998 0.064999998 0.84689999 0.073600002
		 0.84689999 0.0691 0.84609997 0.073600002 0.84609997 0.0691 0.8448 0.073600002 0.8448
		 0.0691 0.84549999 0.066399999 0.84549999 0.18979999 0.84600002 0.18979999 0.84549999
		 0.080700003 0.84600002 0.080700003 0.84560001 0.1943 0.84549999 0.076499999 0.8452
		 0.19329999 0.84500003 0.080700003 0.84500003 0.18979999 0.84649998 0.076899998 0.84490001
		 0.19230001 0.84439999 0.076899998 0.84460002 0.19750001 0.84420002 0.19660001 0.84380001
		 0.19580001 0.84299999 0.1991 0.84399998 0.2001 0.84350002 0.1996 0.84399998 0.2032
		 0.84350002 0.20379999 0.84310001 0.2043 0.84439999 0.2071 0.84460002 0.2058 0.8448
		 0.20460001 0.85089999 0.2044 0.85089999 0.2058 0.85100001 0.2071 0.84399998 0.073600002
		 0.84399998 0.0691 0.84439999 0.064999998 0.84549999 0.064099997 0.84689999 0.073600002
		 0.84649998 0.064999998 0.84689999 0.0691 0.84609997 0.0691 0.84609997 0.073600002
		 0.8448 0.073600002 0.8448 0.0691 0.84549999 0.066399999;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr -s 79 ".vt[0:78]"  -504.84375 6.28435898 437.35961914 -504.65380859 6.37691879 437.6472168
		 -504.76757813 6.28435898 437.76025391 -504.68359375 6.37691116 424.69458008 -504.84375 6.28435135 424.20825195
		 -504.51123047 6.37691116 424.25708008 -504.84375 6.65457916 424.69458008 -505.00390625 6.56203079 437.35961914
		 -504.84375 6.65459061 437.35961914 -505.00390625 6.37691879 437.35961914 -504.88085938 6.37691879 437.87353516
		 -505.00390625 6.37691116 424.69458008 -504.84375 6.28435135 424.69458008 -505.00390625 6.56201935 424.69458008
		 -504.88085938 6.56203079 437.87353516 -504.84375 6.65457916 424.20825195 -505.17626953 6.56201935 424.25708008
		 -504.76757813 6.65459061 437.76025391 -504.68359375 6.56201935 424.69458008 -504.68359375 6.37691879 437.35961914
		 -504.68359375 6.56203079 437.35961914 -505.17626953 6.37691116 424.25708008 -504.65380859 6.56203079 437.6472168
		 -504.51123047 6.56201935 424.25708008 -504.31982422 6.56203079 438.049560547 -504.44091797 6.65459061 438.15112305
		 -504.5625 6.37691879 438.25268555 -504.5625 6.56203079 438.25268555 -504.44091797 6.28435898 438.15112305
		 -504.31982422 6.37691879 438.049560547 -504.075195313 6.37691879 438.43652344 -504.22412109 6.65459061 438.49584961
		 -504.075195313 6.56203079 438.43652344 -504.37304688 6.56203079 438.55517578 -504.37304688 6.37691879 438.55517578
		 -504.22412109 6.28435898 438.49584961 -504.22998047 6.65459061 438.97949219 -504.082519531 6.56203079 439.042480469
		 -504.37744141 6.56203079 438.91625977 -504.37744141 6.37691879 438.91625977 -504.22998047 6.28435898 438.97949219
		 -504.082519531 6.37691879 439.042480469 -504.51757813 6.37691879 439.36474609 -504.58056641 6.28435898 439.21728516
		 -504.51757813 6.56203079 439.36474609 -504.58056641 6.65459061 439.21728516 -504.64404297 6.56203079 439.070068359
		 -504.64404297 6.37691879 439.070068359 -506.59277344 6.56203079 439.3684082 -506.58154297 6.65459061 439.20849609
		 -506.56982422 6.37691879 439.048583984 -506.56982422 6.56203079 439.048583984 -506.58154297 6.28435898 439.20849609
		 -506.59277344 6.37691879 439.3684082 -507.20654297 6.46947098 438.98193359 -504.3828125 6.37691116 423.8659668
		 -504.3828125 6.37691116 423.34155273 -504.3828125 6.56201935 423.8659668 -504.51123047 6.56201935 422.86791992
		 -504.3828125 6.56201935 423.34155273 -504.84375 6.37689972 422.76660156 -504.51123047 6.37689972 422.86791992
		 -505.17626953 6.37689972 422.86791992 -504.84375 6.56201935 422.76660156 -505.31298828 6.56201935 423.8659668
		 -505.31298828 6.56201935 423.34155273 -505.31298828 6.37691116 423.8659668 -505.17626953 6.56201935 422.86791992
		 -505.31298828 6.37691116 423.34155273 -505.051269531 6.28435135 423.8659668 -505.051269531 6.28435135 423.34155273
		 -505.051269531 6.65457916 423.34155273 -505.051269531 6.65457916 423.8659668 -504.62646484 6.65457916 423.8659668
		 -504.62646484 6.28435135 423.8659668 -504.62646484 6.28435135 423.34155273 -504.84375 6.28435135 423.028808594
		 -504.62646484 6.65457916 423.34155273 -504.84375 6.65457916 423.028808594;
	setAttr -s 237 ".ed";
	setAttr ".ed[0:165]"  0 1 1 1 2 1 2 0 0 3 4 1 4 5 1 5 3 0 6 7 1 7 8 1 8 6 0
		 9 2 1 2 10 1 10 9 0 11 4 1 4 12 0 12 11 1 13 9 1 9 7 1 7 13 0 9 14 1 14 7 0 13 15 1
		 15 16 1 16 13 0 11 0 1 0 9 1 9 11 0 7 17 1 17 8 0 18 15 1 15 6 0 6 18 1 12 19 1 19 0 1
		 0 12 0 20 1 1 1 19 0 19 20 1 13 21 1 21 11 0 11 13 1 3 20 1 19 3 0 8 22 1 22 20 0
		 20 8 1 3 23 1 23 18 0 18 3 1 18 8 1 20 18 0 17 24 1 24 22 0 22 17 1 14 25 1 25 17 0
		 17 14 1 14 26 1 26 27 1 27 14 0 10 28 1 28 26 1 26 10 0 2 29 1 29 28 1 28 2 0 22 29 1
		 29 1 0 1 22 0 24 30 1 30 29 0 29 24 1 24 31 1 31 32 1 32 24 0 25 33 1 33 31 1 31 25 0
		 26 33 1 33 27 0 28 34 1 34 26 0 29 35 1 35 28 0 32 36 1 36 37 1 37 32 0 31 38 1 38 36 1
		 36 31 0 34 38 1 38 33 0 33 34 0 35 39 1 39 34 0 34 35 1 30 40 1 40 35 0 35 30 1 32 41 1
		 41 30 0 30 32 0 40 42 1 42 43 1 43 40 0 37 42 1 42 41 0 41 37 0 36 44 1 44 37 0 38 45 1
		 45 36 0 39 46 1 46 38 0 38 39 0 39 43 1 43 47 1 47 39 0 45 48 1 48 44 0 44 45 1 46 49 1
		 49 45 0 45 46 1 46 50 1 50 51 1 51 46 0 47 52 1 52 50 1 50 47 0 43 53 1 53 52 1 52 43 0
		 44 53 1 53 42 0 42 44 0 52 54 0 54 50 0 53 54 0 53 48 0 48 54 0 48 49 1 49 54 0 49 51 1
		 51 54 0 55 23 1 23 5 1 5 55 0 56 57 1 57 55 1 55 56 0 56 58 1 58 59 0 59 56 1 60 58 1
		 58 61 0 61 60 0 62 63 1 63 60 0 60 62 0 64 21 1 21 16 1 16 64 0 65 66 1 66 64 1 64 65 0
		 67 68 1;
	setAttr ".ed[166:236]" 68 65 1 65 67 0 69 21 1 21 66 0 66 69 1 69 68 1 68 70 1
		 70 69 0 71 69 1 70 71 0 72 4 1 4 69 0 69 72 0 4 73 1 73 74 0 74 4 0 5 74 1 74 55 1
		 74 56 1 75 61 1 61 56 0 56 75 1 61 76 1 76 60 1 62 70 1 68 62 0 76 62 1 77 74 1 73 77 0
		 78 75 1 75 77 0 77 78 0 78 70 1 70 76 0 76 78 0 67 71 1 71 78 0 78 67 1 58 77 1 77 59 1
		 78 63 1 63 67 0 78 58 1 58 63 0 59 73 1 73 57 1 57 59 0 73 23 1 23 57 0 72 16 1 15 72 0
		 71 64 1 64 72 1 72 71 0 3 12 1 6 13 1 21 4 1 10 14 1 23 15 1 25 24 1 27 25 1 40 39 1
		 41 40 1 47 46 0 62 67 0 68 66 0 15 4 0 15 73 0 74 75 0 75 76 0 65 71 1;
	setAttr -s 198 ".n";
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
	setAttr ".n[166:197]" -type "float3"  1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20
		 1e+20 1e+20 1e+20 1e+20 1e+20;
	setAttr -s 158 -ch 474 ".fc[0:157]" -type "polyFaces" 
		f 3 0 1 2
		mu 0 3 0 1 2
		f 3 3 4 5
		mu 0 3 3 4 5
		f 3 6 7 8
		mu 0 3 6 7 40
		f 3 9 10 11
		mu 0 3 41 2 8
		f 3 12 13 14
		mu 0 3 9 4 42
		f 3 15 16 17
		mu 0 3 43 41 7
		f 3 18 19 -17
		mu 0 3 41 44 7
		f 3 20 21 22
		mu 0 3 43 45 10
		f 3 23 24 25
		mu 0 3 9 0 41
		f 3 26 27 -8
		mu 0 3 7 46 40
		f 3 28 29 30
		mu 0 3 47 45 6
		f 3 31 32 33
		mu 0 3 42 11 0
		f 3 34 35 36
		mu 0 3 48 1 11
		f 3 37 38 39
		mu 0 3 43 49 9
		f 3 40 -37 41
		mu 0 3 3 48 11
		f 3 42 43 44
		mu 0 3 40 50 48
		f 3 45 46 47
		mu 0 3 3 51 47
		f 3 48 -45 49
		mu 0 3 47 40 48
		f 3 50 51 52
		mu 0 3 46 12 50
		f 3 53 54 55
		mu 0 3 44 13 46
		f 3 56 57 58
		mu 0 3 44 14 52
		f 3 59 60 61
		mu 0 3 8 53 14
		f 3 62 63 64
		mu 0 3 2 54 53
		f 3 65 66 67
		mu 0 3 50 54 1
		f 3 68 69 70
		mu 0 3 12 15 54
		f 3 71 72 73
		mu 0 3 12 16 55
		f 3 74 75 76
		mu 0 3 13 17 16
		f 3 77 78 -58
		mu 0 3 14 17 52
		f 3 79 80 -61
		mu 0 3 53 56 14
		f 3 81 82 -64
		mu 0 3 54 57 53
		f 3 83 84 85
		mu 0 3 55 18 19
		f 3 86 87 88
		mu 0 3 16 20 18
		f 3 89 90 91
		mu 0 3 56 20 17
		f 3 92 93 94
		mu 0 3 57 58 56
		f 3 95 96 97
		mu 0 3 15 59 57
		f 3 98 99 100
		mu 0 3 55 60 15
		f 3 101 102 103
		mu 0 3 59 21 22
		f 3 104 105 106
		mu 0 3 19 21 60
		f 3 107 108 -85
		mu 0 3 18 61 19
		f 3 109 110 -88
		mu 0 3 20 62 18
		f 3 111 112 113
		mu 0 3 58 23 20
		f 3 114 115 116
		mu 0 3 58 22 63
		f 3 117 118 119
		mu 0 3 62 24 61
		f 3 120 121 122
		mu 0 3 23 25 62
		f 3 123 124 125
		mu 0 3 23 26 64
		f 3 126 127 128
		mu 0 3 63 65 26
		f 3 129 130 131
		mu 0 3 22 66 65
		f 3 132 133 134
		mu 0 3 61 66 21
		f 3 -128 135 136
		mu 0 3 26 65 27
		f 3 -131 137 -136
		mu 0 3 65 66 27
		f 3 138 139 -138
		mu 0 3 66 24 27
		f 3 140 141 -140
		mu 0 3 24 25 27
		f 3 142 143 -142
		mu 0 3 25 64 27
		f 3 -125 -137 -144
		mu 0 3 64 26 27
		f 3 144 145 146
		mu 0 3 28 51 5
		f 3 147 148 149
		mu 0 3 29 67 28
		f 3 150 151 152
		mu 0 3 29 30 68
		f 3 153 154 155
		mu 0 3 31 30 69
		f 3 156 157 158
		mu 0 3 32 70 31
		f 3 159 160 161
		mu 0 3 33 49 10
		f 3 162 163 164
		mu 0 3 34 71 33
		f 3 165 166 167
		mu 0 3 72 73 34
		f 3 168 169 170
		mu 0 3 35 49 71
		f 3 171 172 173
		mu 0 3 35 73 36
		f 3 174 -174 175
		mu 0 3 74 35 36
		f 3 176 177 178
		mu 0 3 75 4 35
		f 3 179 180 181
		mu 0 3 4 37 76
		f 3 182 183 -147
		mu 0 3 5 76 28
		f 3 184 -150 -184
		mu 0 3 76 29 28
		f 3 185 186 187
		mu 0 3 38 69 29
		f 3 188 189 -156
		mu 0 3 69 39 31
		f 3 190 -173 191
		mu 0 3 32 36 73
		f 3 -190 192 -159
		mu 0 3 31 39 32
		f 3 193 -181 194
		mu 0 3 77 76 37
		f 3 195 196 197
		mu 0 3 78 38 77
		f 3 198 199 200
		mu 0 3 78 36 39
		f 3 201 202 203
		mu 0 3 72 74 78
		f 3 204 205 -152
		mu 0 3 30 77 68
		f 3 -204 206 207
		mu 0 3 72 78 70
		f 3 -207 208 209
		mu 0 3 70 78 30
		f 3 210 211 212
		mu 0 3 68 37 67
		f 3 213 214 -212
		mu 0 3 37 51 67
		f 3 215 -22 216
		mu 0 3 75 10 45
		f 3 217 218 219
		mu 0 3 74 33 75
		f 3 -33 -36 -1
		mu 0 3 0 11 1
		f 3 220 -14 -4
		mu 0 3 3 42 4
		f 3 221 -18 -7
		mu 0 3 6 43 7
		f 3 -25 -3 -10
		mu 0 3 41 0 2
		f 3 -39 222 -13
		mu 0 3 9 49 4
		f 3 -40 -26 -16
		mu 0 3 43 9 41
		f 3 -12 223 -19
		mu 0 3 41 8 44
		f 3 -222 -30 -21
		mu 0 3 43 6 45
		f 3 -15 -34 -24
		mu 0 3 9 42 0
		f 3 -20 -56 -27
		mu 0 3 7 44 46
		f 3 -47 224 -29
		mu 0 3 47 51 45
		f 3 -221 -42 -32
		mu 0 3 42 3 11
		f 3 -44 -68 -35
		mu 0 3 48 50 1
		f 3 -23 -161 -38
		mu 0 3 43 10 49
		f 3 -48 -50 -41
		mu 0 3 3 47 48
		f 3 -28 -53 -43
		mu 0 3 40 46 50
		f 3 -6 -146 -46
		mu 0 3 3 5 51
		f 3 -31 -9 -49
		mu 0 3 47 6 40
		f 3 -55 225 -51
		mu 0 3 46 13 12
		f 3 -59 226 -54
		mu 0 3 44 52 13
		f 3 -224 -62 -57
		mu 0 3 44 8 14
		f 3 -11 -65 -60
		mu 0 3 8 2 53
		f 3 -2 -67 -63
		mu 0 3 2 1 54
		f 3 -52 -71 -66
		mu 0 3 50 12 54
		f 3 -74 -101 -69
		mu 0 3 12 55 15
		f 3 -226 -77 -72
		mu 0 3 12 13 16
		f 3 -227 -79 -75
		mu 0 3 13 52 17
		f 3 -81 -92 -78
		mu 0 3 14 56 17
		f 3 -83 -95 -80
		mu 0 3 53 57 56
		f 3 -70 -98 -82
		mu 0 3 54 15 57
		f 3 -73 -89 -84
		mu 0 3 55 16 18
		f 3 -76 -91 -87
		mu 0 3 16 17 20
		f 3 -94 -114 -90
		mu 0 3 56 58 20
		f 3 -97 227 -93
		mu 0 3 57 59 58
		f 3 -100 228 -96
		mu 0 3 15 60 59
		f 3 -86 -107 -99
		mu 0 3 55 19 60
		f 3 -229 -106 -102
		mu 0 3 59 60 21
		f 3 -109 -135 -105
		mu 0 3 19 61 21
		f 3 -111 -120 -108
		mu 0 3 18 62 61
		f 3 -113 -123 -110
		mu 0 3 20 23 62
		f 3 -117 229 -112
		mu 0 3 58 63 23
		f 3 -228 -104 -115
		mu 0 3 58 59 22
		f 3 -122 -141 -118
		mu 0 3 62 25 24
		f 3 -126 -143 -121
		mu 0 3 23 64 25
		f 3 -230 -129 -124
		mu 0 3 23 63 26
		f 3 -116 -132 -127
		mu 0 3 63 22 65
		f 3 -103 -134 -130
		mu 0 3 22 21 66
		f 3 -119 -139 -133
		mu 0 3 61 24 66
		f 3 -149 -215 -145
		mu 0 3 28 67 51
		f 3 -153 -213 -148
		mu 0 3 29 68 67
		f 3 -187 -155 -151
		mu 0 3 29 69 30
		f 3 -158 -210 -154
		mu 0 3 31 70 30
		f 3 230 -208 -157
		mu 0 3 32 72 70
		f 3 -164 -170 -160
		mu 0 3 33 71 49
		f 3 -167 231 -163
		mu 0 3 34 73 71
		f 3 -231 -192 -166
		mu 0 3 72 32 73
		f 3 -178 -223 -169
		mu 0 3 35 4 49
		f 3 -171 -232 -172
		mu 0 3 35 71 73
		f 3 -220 -179 -175
		mu 0 3 74 75 35
		f 3 -217 232 -177
		mu 0 3 75 45 4
		f 3 -233 233 -180
		mu 0 3 4 45 37
		f 3 -5 -182 -183
		mu 0 3 5 4 76
		f 3 234 -188 -185
		mu 0 3 76 38 29
		f 3 235 -189 -186
		mu 0 3 38 39 69
		f 3 -193 -200 -191
		mu 0 3 32 39 36
		f 3 -197 -235 -194
		mu 0 3 77 38 76
		f 3 -201 -236 -196
		mu 0 3 78 39 38
		f 3 -203 -176 -199
		mu 0 3 78 74 36
		f 3 -168 236 -202
		mu 0 3 72 34 74
		f 3 -209 -198 -205
		mu 0 3 30 78 77
		f 3 -206 -195 -211
		mu 0 3 68 77 37
		f 3 -234 -225 -214
		mu 0 3 37 45 51
		f 3 -219 -162 -216
		mu 0 3 75 33 10
		f 3 -237 -165 -218
		mu 0 3 74 34 33;
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
	rename -uid "C00CB98B-4491-B834-CCDB-3EBD6618D1A5";
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
connectAttr "Spike_1Shape.iog" "aiStandardSurface1SG.dsm" -na;
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
// End of Spike_1.ma
