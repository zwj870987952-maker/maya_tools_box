//Maya ASCII 2023 scene
//Name: Rock_3_3.ma
//Last modified: Mon, Aug 01, 2022 04:21:27 PM
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
fileInfo "UUID" "72A85966-4D5B-E9B1-6CA6-80AE6E6E74B1";
createNode transform -n "Rock_3_3";
	rename -uid "8D7BF296-400D-F0BF-7871-5392E85BFAE6";
	setAttr ".t" -type "double3" -588.055419921875 1.4534702301025391 -323.6962890625 ;
	setAttr ".rp" -type "double3" 588.055419921875 -1.4534702301025391 323.6962890625 ;
	setAttr ".sp" -type "double3" 588.055419921875 -1.4534702301025391 323.6962890625 ;
createNode mesh -n "Rock_3_3Shape" -p "Rock_3_3";
	rename -uid "28CC441F-4B59-B7B4-576B-A1AD2CA42B83";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 137 ".uvst[0].uvsp[0:136]" -type "float2" 0.62279999 0.71799999
		 0.62370002 0.71799999 0.62370002 0.77579999 0.62269998 0.77579999 0.62550002 0.77579999
		 0.6243 0.77579999 0.6243 0.83990002 0.62510002 0.83990002 0.62379998 0.77579999 0.62489998
		 0.77579999 0.62470001 0.82849997 0.62400001 0.82849997 0.6257 0.71799999 0.62559998
		 0.71799999 0.62559998 0.77579999 0.6257 0.77579999 0.62419999 0.71799999 0.62290001
		 0.71799999 0.62290001 0.77579999 0.62419999 0.77579999 0.625 0.71799999 0.625 0.77579999
		 0.62550002 0.71799999 0.6243 0.71799999 0.62339997 0.8459 0.625 0.84710002 0.62480003
		 0.87580001 0.62370002 0.8757 0.62339997 0.84670001 0.6232 0.84020001 0.6232 0.84670001
		 0.62279999 0.77579999 0.6232 0.83710003 0.6239 0.83279997 0.62330002 0.84619999 0.62510002
		 0.84259999 0.62480003 0.82920003 0.62379998 0.86430001 0.62370002 0.86430001 0.62470001
		 0.86430001 0.62419999 0.86430001 0.6243 0.87599999 0.62470001 0.87599999 0.62419999
		 0.83990002 0.62339997 0.83990002 0.62370002 0.87599999 0.62419999 0.87599999 0.62510002
		 0.84680003 0.62510002 0.84030002 0.62480003 0.87599999 0.6239 0.83249998 0.62339997
		 0.84640002 0.62379998 0.71799999 0.62489998 0.71799999 0.62330002 0.83700001 0.62339997
		 0.78469998 0.6239 0.77079999 0.62470001 0.77109998 0.625 0.78539997 0.62510002 0.88020003
		 0.62510002 0.8829 0.62510002 0.88249999 0.62480003 0.87180001 0.62480003 0.87349999
		 0.62370002 0.90109998 0.62370002 0.903 0.62370002 0.90170002 0.62370002 0.90189999
		 0.62480003 0.90109998 0.62480003 0.903 0.62480003 0.90200001 0.62480003 0.90179998
		 0.6257 0.80220002 0.6257 0.83840001 0.62559998 0.83840001 0.62559998 0.80220002 0.62489998
		 0.83840001 0.62489998 0.80220002 0.625 0.80220002 0.625 0.83840001 0.62279999 0.80220002
		 0.62279999 0.83840001 0.62290001 0.83840001 0.62290001 0.80220002 0.62379998 0.80220002
		 0.62379998 0.83840001 0.62370002 0.83840001 0.62370002 0.80220002 0.62550002 0.80220002
		 0.62550002 0.83840001 0.62400001 0.8714 0.62470001 0.8714 0.62470001 0.87309998 0.6239
		 0.87309998 0.62510002 0.87849998 0.62510002 0.87870002 0.62510002 0.88279998 0.62339997
		 0.87849998 0.6232 0.87669998 0.6239 0.87400001 0.62419999 0.90109998 0.62419999 0.903
		 0.62470001 0.90109998 0.6243 0.90109998 0.6243 0.903 0.62470001 0.903 0.62370002
		 0.90090001 0.62480003 0.90090001 0.625 0.88300002 0.62339997 0.8822 0.62339997 0.88270003
		 0.62330002 0.87669998 0.62269998 0.83840001 0.62330002 0.88239998 0.6232 0.88270003
		 0.62339997 0.88249999 0.62559998 0.71799999 0.62559998 0.77579999 0.62269998 0.77579999
		 0.62470001 0.86430001 0.62480003 0.87599999 0.62370002 0.87599999 0.62370002 0.87599999
		 0.62480003 0.87180001 0.62370002 0.90109998 0.62370002 0.903 0.62480003 0.90109998
		 0.62480003 0.903 0.62559998 0.83840001 0.62559998 0.80220002 0.62370002 0.90109998
		 0.62470001 0.903 0.62269998 0.83840001 0.62279999 0.80220002 0.62279999 0.80220002
		 0.62279999 0.71799999 0.62279999 0.71799999;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr -s 57 ".vt[0:56]"  587.57861328 -1.45347023 314.11181641 577.73876953 -1.45347023 320.42626953
		 577.72460938 5.0011291504 320.40454102 587.59277344 5.0011291504 313.15844727 596.47412109 5.0011291504 333.62060547
		 598.95263672 5.0011291504 324.095703125 595.53076172 12.16213989 324.19824219 593.97802734 12.16214752 330.32568359
		 577.37841797 5.0011291504 321.050048828 577.15820313 5.0011291504 329.29711914 582.26806641 10.88832092 327.56933594
		 582.40966797 10.88832092 322.26782227 585.90185547 -1.45347023 334.44213867 595.953125 -1.45347023 334.035644531
		 595.95263672 5.0011291504 334.035644531 585.90185547 5.0011291504 334.44213867 598.95263672 -1.45347023 324.095703125
		 595.75537109 -1.45347023 314.34106445 595.75585938 5.0011291504 314.34179688 577.51074219 -1.45347023 329.90673828
		 585.14990234 -1.45347023 334.25976563 585.14990234 5.0011291504 334.25976563 577.51123047 5.0011291504 329.90722656
		 596.47412109 -1.45347023 333.62133789 587.068847656 12.88169098 318.35742188 585.73974609 12.97039795 330.010498047
		 587.39160156 16.16772461 327.97241211 588.29736328 16.16297913 320.45874023 587.68798828 12.91783142 317.9855957
		 593.091796875 11.84170532 317.30981445 587.68798828 12.91782379 317.071533203 595.22460938 5.0011291504 313.89599609
		 588.34179688 5.0011291504 312.95043945 583.041015625 11.34558868 321.63623047 587.0092773438 12.86128998 317.33984375
		 585.39111328 12.45456696 330.41870117 582.53369141 11.0065536499 328.27197266 591.15380859 16.53164673 320.66479492
		 588.82519531 16.53164673 320.64160156 587.97509766 16.53164673 327.78320313 591.41992188 16.53164673 327.64379883
		 592.35693359 16.53164673 324.20410156 592.87646484 16.19520569 324.19482422 592.00048828125 16.19613647 327.83642578
		 593.51416016 12.16213989 317.91552734 591.72314453 16.1942749 320.45068359 586.083007813 12.93065643 330.48217773
		 593.43847656 12.20465851 330.71166992 591.48144531 16.19630432 328.25268555 587.77490234 16.1932373 328.39770508
		 577.37841797 -1.45347023 321.050048828 577.15820313 -1.45347023 329.29736328 588.77490234 16.19395447 320.033935547
		 591.16503906 16.19581604 320.054931641 582.87255859 11.38166046 327.67382813 595.22119141 -1.45347023 313.9465332
		 588.34570313 -1.45347023 313.87792969;
	setAttr -s 109 ".ed[0:108]"  0 1 0 1 2 1 2 3 0 3 0 1 4 5 1 5 6 1 6 7 1
		 7 4 0 8 9 0 9 10 1 10 11 1 11 8 1 12 13 0 13 14 0 14 15 1 15 12 1 16 17 0 17 18 0
		 18 5 1 5 16 0 19 20 0 20 21 1 21 22 1 22 19 0 23 16 0 4 23 0 24 25 0 25 26 0 26 27 0
		 27 24 0 28 29 0 29 30 0 30 28 1 31 32 0 32 30 1 29 31 1 2 33 1 33 34 0 34 3 1 21 35 1
		 35 36 0 36 22 1 37 38 1 38 39 0 39 40 1 40 41 0 41 37 0 6 42 1 42 43 1 43 7 0 6 44 1
		 44 45 0 45 42 1 46 47 1 47 48 0 48 49 1 49 46 0 33 24 1 24 34 1 50 51 0 51 9 0 8 50 1
		 14 47 0 46 15 1 18 44 1 28 52 0 52 53 1 53 29 1 33 54 1 54 25 1 35 46 0 46 25 1 25 35 1
		 36 54 1 54 10 1 10 36 1 53 37 1 37 45 1 45 53 1 52 27 1 27 38 1 38 52 1 49 39 1 39 26 1
		 26 49 1 48 43 1 43 40 1 40 48 1 15 21 1 20 12 0 51 19 0 22 9 0 55 31 0 31 18 0 17 55 0
		 8 2 0 1 50 0 13 23 0 4 14 0 33 11 1 7 47 1 29 44 1 41 42 1 28 24 0 34 30 0 32 3 0
		 32 56 1 56 0 0 55 56 0;
	setAttr -s 93 ".n[0:92]" -type "float3"  1e+20 1e+20 1e+20 1e+20 1e+20
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
		 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20 1e+20;
	setAttr -s 53 -ch 205 ".fc[0:52]" -type "polyFaces" 
		f 4 0 1 2 3
		mu 0 4 0 1 2 3
		f 4 4 5 6 7
		mu 0 4 4 5 6 7
		f 4 8 9 10 11
		mu 0 4 8 9 10 11
		f 4 12 13 14 15
		mu 0 4 12 13 14 15
		f 4 16 17 18 19
		mu 0 4 16 17 18 19
		f 4 20 21 22 23
		mu 0 4 20 116 117 21
		f 4 24 -20 -5 25
		mu 0 4 22 23 5 4
		f 4 26 27 28 29
		mu 0 4 24 25 26 27
		f 3 30 31 32
		mu 0 3 28 29 30
		f 4 33 34 -32 35
		mu 0 4 31 118 30 32
		f 4 -3 36 37 38
		mu 0 4 3 2 33 34
		f 4 -23 39 40 41
		mu 0 4 21 117 35 36
		f 5 42 43 44 45 46
		mu 0 5 37 38 39 119 40
		f 4 -7 47 48 49
		mu 0 4 7 6 41 42
		f 4 50 51 52 -48
		mu 0 4 43 44 45 46
		f 4 53 54 55 56
		mu 0 4 47 48 49 120
		f 3 57 58 -38
		mu 0 3 50 51 34
		f 4 59 60 -9 61
		mu 0 4 52 53 9 8
		f 4 -15 62 -54 63
		mu 0 4 15 14 48 47
		f 4 -19 64 -51 -6
		mu 0 4 19 18 44 43
		f 4 -31 65 66 67
		mu 0 4 54 28 121 122
		f 4 -58 68 69 -27
		mu 0 4 55 56 57 58
		f 3 70 71 72
		mu 0 3 59 60 61
		f 3 73 74 75
		mu 0 3 62 63 123
		f 3 76 77 78
		mu 0 3 64 65 66
		f 3 79 80 81
		mu 0 3 124 67 125
		f 3 82 83 84
		mu 0 3 68 69 70
		f 3 85 86 87
		mu 0 3 126 71 127
		f 4 -16 88 -22 89
		mu 0 4 72 73 74 75
		f 4 -61 90 -24 91
		mu 0 4 76 77 78 79
		f 4 92 93 -18 94
		mu 0 4 80 81 82 83
		f 4 -62 95 -2 96
		mu 0 4 84 85 86 87
		f 4 -14 97 -26 98
		mu 0 4 128 129 88 89
		f 4 -41 -73 -70 -74
		mu 0 4 62 59 61 63
		f 4 -11 -75 -69 99
		mu 0 4 90 91 92 93
		f 4 -8 100 -63 -99
		mu 0 4 89 94 95 128
		f 4 -40 -89 -64 -71
		mu 0 4 59 74 73 96
		f 4 -65 -94 -36 101
		mu 0 4 97 82 81 98
		f 4 -10 -92 -42 -76
		mu 0 4 91 76 79 62
		f 4 -12 -100 -37 -96
		mu 0 4 85 90 99 86
		f 4 -67 -82 -43 -77
		mu 0 4 64 124 125 65
		f 4 -56 -88 -45 -83
		mu 0 4 68 126 127 69
		f 4 -53 -78 -47 102
		mu 0 4 100 130 65 101
		f 4 -49 -103 -46 -87
		mu 0 4 102 103 104 105
		f 4 -29 -84 -44 -81
		mu 0 4 106 107 131 125
		f 4 -55 -101 -50 -86
		mu 0 4 126 95 94 102
		f 4 -28 -72 -57 -85
		mu 0 4 107 108 96 68
		f 4 -30 -80 -66 103
		mu 0 4 109 106 124 110
		f 4 -52 -102 -68 -79
		mu 0 4 130 97 111 64
		f 4 -39 104 -35 105
		mu 0 4 112 113 114 132
		f 4 106 107 -4 -106
		mu 0 4 132 133 134 112
		f 4 -59 -104 -33 -105
		mu 0 4 113 115 110 114
		f 4 108 -107 -34 -93
		mu 0 4 135 136 118 31;
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
connectAttr "Rock_3_3Shape.iog" "aiStandardSurface1SG.dsm" -na;
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
// End of Rock_3_3.ma
