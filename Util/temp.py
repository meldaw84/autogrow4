import glob
import os
import sys
import rdkit
import rdkit.Chem as Chem
import rdkit.Chem.AllChem as AllChem
import support_scripts.Multiprocess as mp
import pickle

reactions = {
	"1_Pictet_Spengler": {
		"reaction_string": "[cH1:1]1:[c:2](-[CH2:7]-[CH2:8]-[NH2:9]):[c:3]:[c:4]:[c:5]:[c:6]:1.[#6:11]-[C;R0:10]=[OD1]>>[c:1]12:[c:2](-[CH2:7]-[CH2:8]-[NH1:9]-[C:10]-2(-[#6:11])):[c:3]:[c:4]:[c:5]:[c:6]:1",
		"functional_groups": ["beta_arylethylamine", "aldehyde_or_ketone"],
		"group_smarts": ["[cH1]1:[c](-[CH2]-[CH2]-[NH2]):[c]:[c]:[c]:[c]:1", "[#6]-[C;R0]=[OD1]"],
		"example_reactants": ["c1cc(CCN)ccc1", "CC(=O)"],
		"num_reactants": 2,
		"RXN_NUM": 1
	},
	"2_benzimidazole_derivatives_carboxylic_acid_ester": {
		"reaction_string": "[c;r6:1](-[NH1;$(N-[#6]):2]):[c;r6:3](-[NH2:4]).[#6:6]-[C;R0:5](=[OD1])-[#8;H1,$(O-[CH3])]>>[c:3]1:[c:1]:[n:2]:[c:5](-[#6:6]):[n:4]:1",
		"functional_groups": ["ortho_phenylenediamine", "carboxylic_acid_or_ester"],
		"group_smarts": ["[c;r6](-[NH1;$(N-[#6])]):[c;r6](-[NH2])", "[CH0;$(C-[#6]);R0](=[OD1])-[#8;H1,$(O-[CH3]),$(O-[CH2]-[CH3])]"],
		"example_reactants": ["c1c(NC)c(N)ccc1", "CC(=O)O"],
		"num_reactants": 2,
		"RXN_NUM": 2
	},
	"3_benzimidazole_derivatives_aldehyde": {
		"reaction_string": "[c;r6:1](-[NH1;$(N-[#6]):2]):[c;r6:3](-[NH2:4]).[#6:6]-[CH1;R0:5](=[OD1])>>[c:3]1:[c:1]:[n:2]:[c:5](-[#6:6]):[n:4]:1",
		"functional_groups": ["ortho_phenylenediamine", "aldehyde"],
		"group_smarts": ["[c;r6](-[NH1;$(N-[#6])]):[c;r6](-[NH2])", "[#6]-[CH1;R0](=[OD1])"],
		"example_reactants": ["c1c(NC)c(N)ccc1", "CC(=O)"],
		"num_reactants": 2,
		"RXN_NUM": 3
	},
	"4_benzothiazole": {
		"reaction_string": "[c;r6:1](-[SH1:2]):[c;r6:3](-[NH2:4]).[#6:6]-[CH1;R0:5](=[OD1])>>[c:3]1:[c:1]:[s:2]:[c:5](-[#6:6]):[n:4]:1",
		"functional_groups": ["ortho_aminothiophenol", "aldehyde"],
		"group_smarts": ["[#16;H1]-[c;r6][c;r6]-[#7]", "[#6]-[CH1;R0](=[OD1])"],
		"example_reactants": ["c1c(S)c(N)ccc1", "CC(=O)"],
		"num_reactants": 2,
		"RXN_NUM": 4
	},
	"5_benzoxazole_arom_aldehyde": {
		"reaction_string": "[c:1](-[OH1;$(Oc1ccccc1):2]):[c;r6:3](-[NH2:4]).[c:6]-[CH1;R0:5](=[OD1])>>[c:3]1:[c:1]:[o:2]:[c:5](-[c:6]):[n:4]:1",
		"functional_groups": ["ortho_aminophenol", "aryl_aldehyde"],
		"group_smarts": ["[c](-[OH1;$(Oc1ccccc1)]):[c;r6](-[NH2])", "[c]-[CH1;R0](=[OD1])"],
		"example_reactants": ["c1cc(O)c(N)cc1", "c1ccccc1C(=O)"],
		"num_reactants": 2,
		"RXN_NUM": 5
	},
	"6_benzoxazole_carboxylic_acid": {
		"reaction_string": "[c;r6:1](-[OH1:2]):[c;r6:3](-[NH2:4]).[#6:6]-[C;R0:5](=[OD1])-[OH1]>>[c:3]1:[c:1]:[o:2]:[c:5](-[#6:6]):[n:4]:1",
		"functional_groups": ["ortho_1amine_2alcohol_arylcyclic", "carboxylic_acid"],
		"group_smarts": ["[c;r6](-[OH1]):[c;r6](-[NH2])", "[C;$(C=O)][OH1]"],
		"example_reactants": ["c1cc(O)c(N)cc1", "CC(=O)O"],
		"num_reactants": 2,
		"RXN_NUM": 6
	},
	"7_thiazole": {
		"reaction_string": "[#6:6]-[#6:1](~[#8])-[#6:5](-[#6:7])-[#17,#35,#53].[NH2:2]-[C:3]=[SD1:4]>>[c:1]2(-[#6:6]):[n:2]:[c:3]:[s:4][c:5]([#6:7]):2",
		"functional_groups": ["haloketone", "thioamide"],
		"group_smarts": ["[#6]-[#6](~[#8])-[#6](-[#6])-[#17,#35,#53]", "[NH2]-[C]=[SD1]"],
		"example_reactants": ["CC(=O)C(I)C", "NC(=S)C"],
		"num_reactants": 2,
		"RXN_NUM": 7
	},
	"8_Niementowski_quinazoline": {
		"reaction_string": "[c:1](-[C;$(C-c1ccccc1):2](=[OD1:3])-[OH1]):[c:4](-[NH2:5]).[N;!H0;!$(N-N);!$(N-C=N);!$(N(-C=O)-C=O):6]-[C;H1,$(C-[#6]):7]=[OD1]>>[c:4]2:[c:1]-[C:2](=[O:3])-[N:6]-[C:7]=[N:5]-2",
		"functional_groups": ["anthranilic_acid", "amide"],
		"group_smarts": ["[c](-[C;$(C-c1ccccc1)](=[OD1])-[OH1]):[c](-[NH2])", "[N;!H0;!$(N-N);!$(N-C=N);!$(N(-C=O)-C=O)]-[C;H1,$(C-[#6])]=[OD1]"],
		"example_reactants": ["c1c(C(=O)O)c(N)ccc1", "C(=O)N"],
		"num_reactants": 2,
		"RXN_NUM": 8
	},
	"9_tetrazole_terminal": {
		"reaction_string": "[C;$(C-[#6]):1]#[NH0:2]>>[C:1]1=[N:2]-N-N=N-1",
		"functional_groups": ["nitrile"],
		"group_smarts": ["[#6]#[#7]"],
		"example_reactants": ["CC#N"],
		"num_reactants": 1,
		"RXN_NUM": 9
	},
	"10_tetrazole_connect_regioisomere_1": {
		"reaction_string": "[C;$(C-[#6]):1]#[N:2].[C;A;!$(C=O):3]-[*;#17,#35,#53]>>[C:1]1=[N:2]-N(-[C:3])-N=N-1",
		"functional_groups": ["nitrile", "alkyl_halogen"],
		"group_smarts": ["[#6]#[#7]", "[C;A;!$(C=O)]-[*;#17,#35,#53]"],
		"example_reactants": ["CC#N", "CBr"],
		"num_reactants": 2,
		"RXN_NUM": 10
	},
	"11_tetrazole_connect_regioisomere_2": {
		"reaction_string": "[C;$(C-[#6]):1]#[N:2].[C;A;!$(C=O):3]-[*;#17,#35,#53]>>[C:1]1=[N:2]-N=N-N-1(-[C:3])",
		"functional_groups": ["nitrile", "alkyl_halogen"],
		"group_smarts": ["[#6]#[#7]", "[C;A;!$(C=O)]-[*;#17,#35,#53]"],
		"example_reactants": ["CC#N", "CBr"],
		"num_reactants": 2,
		"RXN_NUM": 11
	},
	"12_Huisgen_Cu_catalyzed_1_4_subst": {
		"reaction_string": "[C;H0:1]#[C;H1:2].[C;H1,H2;A;!$(C=O):3]-[*;#17,#35,#53,OH1]>>[C:1]1=[C:2]-N(-[C:3])-N=N-1",
		"functional_groups": ["alkyne", "alkyl_halogen_or_alcohol"],
		"group_smarts": ["[#6]#[#6]", "[C;H1,H2;A;!$(C=O)]-[*;#17,#35,#53,OH1]"],
		"example_reactants": ["CC#C", "CCBr"],
		"num_reactants": 2,
		"RXN_NUM": 12
	},
	"13_Huisgen_Ru_catalyzed_1_5_subst": {
		"reaction_string": "[C;H0:1]#[C;H1:2].[C;H1,H2;A;!$(C=O):3]-[*;#17,#35,#53,OH1]>>[C:1]1=[C:2]-N=NN(-[C:3])-1",
		"functional_groups": ["alkyne", "alkyl_halogen_or_alcohol"],
		"group_smarts": ["[#6]#[#6]", "[C;H1,H2;A;!$(C=O)]-[*;#17,#35,#53,OH1]"],
		"example_reactants": ["CC#C", "CCBr"],
		"num_reactants": 2,
		"RXN_NUM": 13
	},
	"14_Huisgen_disubst_alkyne": {
		"reaction_string": "[C;H0:1]#[C;H0:2].[C;H1,H2;A;!$(C=O):3]-[*;#17,#35,#53,OH1]>>[C:1]1=[C:2]-N=NN(-[C:3])-1",
		"functional_groups": ["alkyne", "alkyl_halogen_or_alcohol"],
		"group_smarts": ["[#6]#[#6]", "[C;H1,H2;A;!$(C=O)]-[*;#17,#35,#53,OH1]"],
		"example_reactants": ["CC#CC", "CCBr"],
		"num_reactants": 2,
		"RXN_NUM": 14
	},
	"15_1_2_4_triazole_acetohydrazide": {
		"reaction_string": "[#6;$(C-[#6]):1]#[#7:2].[#7:3]-[#7:4]-[#6:5]=[#8]>>[N:2]1-[#6:1]=[#7:3]-[#7:4]-[#6:5]=1",
		"functional_groups": ["nitrile", "acetohydrazide"],
		"group_smarts": ["[#6]#[#7]", "[#7]-[#7]-[#6]=[#8]"],
		"example_reactants": ["CC#N", "NNC(=O)C"],
		"num_reactants": 2,
		"RXN_NUM": 15
	},
	"16_1_2_4_triazole_carboxylic_acid_ester": {
		"reaction_string": "[C;$(C-[#6]):1]#[N:2].[CH0;$(C-[#6]);R0:5](=[OD1])-[#8;H1,$(O-[CH3]),$(O-[CH2]-[CH3])]>>[N:2]1-[C:1]=N-N-[C:5]=1",
		"functional_groups": ["nitrile", "carboxylic_acid_or_ester"],
		"group_smarts": ["[#6]#[#7]", "[CH0;$(C-[#6]);R0](=[OD1])-[#8;H1,$(O-[CH3]),$(O-[CH2]-[CH3])]"],
		"example_reactants": ["CC#N", "OC(=O)C"],
		"num_reactants": 2,
		"RXN_NUM": 16
	},
	"17_3_nitrile_pyridine": {
		"reaction_string": "[#6;!$([#6](-C=O)-C=O):4]-[CH0:1](=[OD1])-[C;H1&!$(C-[*;!#6])&!$(C-C(=O)O),H2:2]-[CH0;R0:3](=[OD1])-[#6;!$([#6](-C=O)-C=O):5]>>[c:1]1(-[#6:4]):[c:2]:[c:3](-[#6:5]):n:c(-O):c(-C#N):1",
		"functional_groups": ["beta_dicarbonyl"],
		"group_smarts": ["[#6;!$([#6](-C=O)-C=O)]-[CH0](=[OD1])-[C;H1&!$(C-[*;!#6])&!$(C-C(=O)O),H2]-[CH0;R0](=[OD1])-[#6;!$([#6](-C=O)-C=O)]"],
		"example_reactants": ["CC(=O)CC(=O)C"],
		"num_reactants": 1,
		"RXN_NUM": 17
	},
	"18_spiro_chromanone": {
		"reaction_string": "[c:1](-[C;$(C-c1ccccc1):2](=[OD1:3])-[CH3:4]):[c:5](-[OH1:6]).[C;$(C1-[CH2]-[CH2]-[N,C]-[CH2]-[CH2]-1):7](=[OD1])>>[O:6]1-[c:5]:[c:1]-[C:2](=[OD1:3])-[C:4]-[C:7]-1",
		"functional_groups": ["2_acetylphenol", "cyclohexanone"],
		"group_smarts": ["[c](-[C;$(C-c1ccccc1)](=[OD1])-[CH3]):[c](-[OH1])", "[C;$(C1-[CH2]-[CH2]-[N,C]-[CH2]-[CH2]-1)](=[OD1])"],
		"example_reactants": ["c1cc(C(=O)C)c(O)cc1", "C1(=O)CCNCC1"],
		"num_reactants": 2,
		"RXN_NUM": 18
	},
	"19_pyrazole": {
		"reaction_string": "[#6;!$([#6](-C=O)-C=O):4]-[CH0:1](=[OD1])-[C;H1&!$(C-[*;!#6])&!$(C-C(=O)O),H2:2]-[CH0;R0:3](=[OD1])-[#6;!$([#6](-C=O)-C=O):5].[#7:6]-[#7:7]>>[C:1]1(-[#6:4])-[C:2]=[C:3](-[#6:5])-[#7:7]-[#7:6]=1",
		"functional_groups": ["beta_dicarbonyl", "hydrazine"],
		"group_smarts": ["[#6;!$([#6](-C=O)-C=O)]-[CH0](=[OD1])-[C;H1&!$(C-[*;!#6])&!$(C-C(=O)O),H2]-[CH0;R0](=[OD1])-[#6;!$([#6](-C=O)-C=O)]", "[#7:3]-[#7:3]"],
		"example_reactants": ["CC(=O)CC(=O)C", "NNC"],
		"num_reactants": 2,
		"RXN_NUM": 19
	},
	"20_phthalazinone": {
		"reaction_string": "[c;r6:1](-[C;$(C=O):6]-[OH1])[c;r6:2][C:3]=[#8].[#7:4]-[#7:5]>>[c:1]1:[c:2]-[C:3]=[#7:4]-[#7:5]-[C:6]-1",
		"functional_groups": ["phthalazinone_precursor", "hydrazine"],
		"group_smarts": ["[c;r6]([C](=[OD1])[#8])[c;r6][C]=[#8]", "[#7:3]-[#7:3]"],
		"example_reactants": ["c1cc(C(=O)O)c(C(=O)C)cc1", "NNC"],
		"num_reactants": 2,
		"RXN_NUM": 20
	},
	"21_Paal_Knorr_pyrrole": {
		"reaction_string": "[#6:1](=[#8])[#6:2][#6:3][#6:4](=[#8]).[NH2;$(N-[C,N]);!$(NC=[O,S,N]);!$(N([#6])[#6]);!$(N~N~N):5]>>[C:1]1=[C:2]-[C:3]=[C:4]-[N:5]-1",
		"functional_groups": ["1_4_dione", "primary_amine"],
		"group_smarts": ["[#6](=[#8])[#6][#6][#6](=[#8])", "[NH2;$(N-[C,N]);!$(NC=[O,S,N]);!$(N([#6])[#6]);!$(N~N~N)]"],
		"example_reactants": ["CC(=O)CCC(=O)C", "NC"],
		"num_reactants": 2,
		"RXN_NUM": 21
	},
	"22_triaryl_imidazole": {
		"reaction_string": "[C;$(C-a):1](~[#8;D0,D1])[C;$(C-a):2](~[#8;D0,D1]).[CH1;R0;$(C-a):3](=[OD1])>>[C:1]1-N=[C:3]-[NH1]-[C:2]=1",
		"functional_groups": ["benzil_or_benzoin", "aryl_aldehyde"],
		"group_smarts": ["[c;R][C](~[#8;D0,D1])[C](~[#8;D0,D1])[c;R]", "[c]-[CH1;R0](=[OD1])"],
		"example_reactants": ["c1ccccc1C(=O)C(=O)c1ccccc1", "c1ccccc1C(=O)"],
		"num_reactants": 2,
		"RXN_NUM": 22
	},
	"23_Fischer_indole": {
		"reaction_string": "[#7;$(N-c1ccccc1):1](-[#7])-[c:5]:[cH1:4].[#6:3]-[C:2]=[OD1]>>[C:5]1-[#7:1]-[C:2]=[C:3]-[C:4]:1",
		"functional_groups": ["phenylhydrazine", "aldehyde_or_ketone"],
		"group_smarts": ["[#7;$(N-c1ccccc1)](-[#7])-[c]:[cH1]", "[#6]-[C;R0]=[OD1]"],
		"example_reactants": ["c1ccccc1NN", "CCC(=O)C"],
		"num_reactants": 2,
		"RXN_NUM": 23
	},
	"24_Friedlaender_chinoline": {
		"reaction_string": "[#7:1]-[c:2]:[c:3]-[#6:4]~[#8;D0,D1].[C;$(C([#6])[#6]):6](=[OD1])-[CH2;$(C([#6])[#6]);!$(C(C=O)C=O):5]>>[#7:1]1-[c:2]:[c:3]-[C:4]=[C:5]-[C:6]:1",
		"functional_groups": ["ortho_aminobenzaldehyde", "ketone"],
		"group_smarts": ["[#7]-[c][c]-[#6]~[#8;D0,D1]", "[C;$(C([#6])[#6])](=[OD1])-[CH2;$(C([#6])[#6]);!$(C(C=O)C=O)]"],
		"example_reactants": ["c1cccc(C=O)c1N", "CCC(=O)C"],
		"num_reactants": 2,
		"RXN_NUM": 24
	},
	"25_benzofuran": {
		"reaction_string": "[*;Br,I;$(*c1ccccc1)]-[c:1]:[c:2]-[OH1:3].[C;H0:4]#[C;H1:5]>>[c:1]1:[c:2]-[O:3]-[C:4]=[C:5]-1",
		"functional_groups": ["ortho_halo_phenol", "alkyne"],
		"group_smarts": ["[*;Br,I;$(*c1ccccc1)]-[c]:[c]-[OH1]", "[#6]#[#6]"],
		"example_reactants": ["c1cc(I)c(O)cc1", "CC#C"],
		"num_reactants": 2,
		"RXN_NUM": 25
	},
	"26_benzothiophene": {
		"reaction_string": "[*;Br,I]-[c:1]:[c:2]-[S:3]-[C].[C;H0:4]#[C;H1:5]>>[c:1]1:[c:2]-[S:3]-[C:4]=[C:5]-1",
		"functional_groups": ["aminobenzenethiol", "alkyne"],
		"group_smarts": ["[*;Br,I]-[c][c]-[S]-[C]", "[#6]#[#6]"],
		"example_reactants": ["c1cc(I)c(SC)cc1", "CC#C"],
		"num_reactants": 2,
		"RXN_NUM": 26
	},
	"27_indole": {
		"reaction_string": "[*;Br,I;$(*c1ccccc1)]-[c:1]:[c:2]-[NH2:3].[C;H0:4]#[C;H1:5]>>[c:1]1:[c:2]-[N:3]-[C:4]=[C:5]-1",
		"functional_groups": ["ortho_halo_thioanizole", "alkyne"],
		"group_smarts": ["[*;Br,I;$(*c1ccccc1)]-[c]:[c]-[NH2]", "[#6]#[#6]"],
		"example_reactants": ["c1cc(I)c(N)cc1", "CC#C"],
		"num_reactants": 2,
		"RXN_NUM": 27
	},
	"28_oxadiazole": {
		"reaction_string": "[#6:6][C:5]#[#7:4].[#6:1][C:2](=[OD1:3])[OH1]>>[#6:6][c:5]1[n:4][o:3][c:2]([#6:1])n1",
		"functional_groups": ["nitrile", "carboxylic_acid"],
		"group_smarts": ["[#6]#[#7]", "[C;$(C=O)][OH1]"],
		"example_reactants": ["CC#N", "CC(=O)O"],
		"num_reactants": 2,
		"RXN_NUM": 28
	},
	"29_Williamson_ether": {
		"reaction_string": "[#6;$([#6]~[#6]);!$([#6]=O):2][#8;H1:3].[Cl,Br,I][#6,H2:4]>>[#6:4][O:3][#6:2]",
		"functional_groups": ["alcohol", "alkyl_halide"],
		"group_smarts": ["[C]~[#8;H1]", "[Cl,Br,I]-[#6,H2]"],
		"example_reactants": ["CCO", "CCBr"],
		"num_reactants": 2,
		"RXN_NUM": 29
	},
	"30_reductive_amination": {
		"reaction_string": "[#6:4]-[C:1]=[OD1].[#7;H1,H2:3]-[C:5]>>[#6:4][C:1]-[N:3]-[C:5]",
		"functional_groups": ["aldehyde_or_ketone", "primary_or_secondary_amine"],
		"group_smarts": ["[#6]-[C;R0]=[OD1]", "[#7;H1,H2]"],
		"example_reactants": ["CC(=O)", "NC"],
		"num_reactants": 2,
		"RXN_NUM": 30
	},
	"31_Suzuki": {
		"reaction_string": "[#6:1][#5]([#8])[#8].[a;H0;D3;$([#6](~[#6])~[#6]):2][Cl,Br,I]>>[a:2][#6:1]",
		"functional_groups": ["boronic_acid", "aryl_halide"],
		"group_smarts": ["[#6][#5]([#8])[#8]", "[Cl,Br,I][a]"],
		"example_reactants": ["c1ccccc1B(O)O", "c1ccccc1Br"],
		"num_reactants": 2,
		"RXN_NUM": 31
	},
	"32_piperidine_indole": {
		"reaction_string": "[c;H1:3]1:[c:4]:[c:5]:[c;H1:6]:[c:7]2:[#7:8]:[c:9]:[c;H1:1]:[c:2]:1:2.O=[C:10]1[#6;H2:11][#6;H2:12][#7:13][#6;H2:14][#6;H2:15]1>>[#6;H2:12]3[#6;H1:11]=[C:10]([c:1]1:[c:9]:[#7:8]:[c:7]2:[c:6]:[c:5]:[c:4]:[c:3]:[c:2]:1:2)[#6;H2:15][#6;H2:14][#7:13]3",
		"functional_groups": ["indole", "4_piperidone"],
		"group_smarts": ["[c;H1]1:[c]:[c]:[c;H1]:[c]2:[nH]:[c]:[c;H1]:[c]:1:2", "O=[C]1[#6;H2][#6;H2][N][#6;H2][#6;H2]1"],
		"example_reactants": ["c1cccc2c1C=CN2", "C1CC(=O)CCN1"],
		"num_reactants": 2,
		"RXN_NUM": 32
	},
	"33_Negishi": {
		"reaction_string": "[#6;$([#6]~[#6]);!$([#6]~[S,N,O,P]):1][Cl,Br,I].[Cl,Br,I][#6;$([#6]~[#6]);!$([#6]~[S,N,O,P]):2]>>[#6:2][#6:1]",
		"functional_groups": ["halide", "halide"],
		"group_smarts": ["[#6][#6][Cl,Br,I]", "[#6][#6][Cl,Br,I]"],
		"example_reactants": ["CCBr", "CCBr"],
		"num_reactants": 2,
		"RXN_NUM": 33
	},
	"34_Mitsunobu_imide": {
		"reaction_string": "[C:1][OH1][OH1].[NH1;$(N(C=O)C=O):2]>>[C:1][N:2]",
		"functional_groups": ["alcohol", "imide"],
		"group_smarts": ["[C]~[#8;H1]", "[NH1;$(N(C=O)C=O)]"],
		"example_reactants": ["CC(O)C", "CC(=O)NC(=O)C"],
		"num_reactants": 2,
		"RXN_NUM": 34
	},
	"35_Mitsunobu_phenole": {
		"reaction_string": "[C:1][OH1][OH1].[OH1;$(Oc1ccccc1):2]>>[C:1][O:2]",
		"functional_groups": ["alcohol", "phenole"],
		"group_smarts": ["[C]~[#8;H1]", "[OH1;$(Oc1ccccc1)]"],
		"example_reactants": ["CC(O)C", "c1ccccc1O"],
		"num_reactants": 2,
		"RXN_NUM": 35
	},
	"36_Mitsunobu_sulfonamide": {
		"reaction_string": "[C:1][OH1][OH1].[NH1;$(N([#6])[#16](=O)=O):2]>>[C:1][N:2]",
		"functional_groups": ["alcohol", "sulfonamide"],
		"group_smarts": ["[C]~[#8;H1]", "[NH1;$(N([#6])[#16](=O)=O)]"],
		"example_reactants": ["CC(O)C", "CNS(=O)(=O)C"],
		"num_reactants": 2,
		"RXN_NUM": 36
	},
	"37_Mitsunobu_tetrazole_1": {
		"reaction_string": "[C:1][OH1][OH1].[#7H1:2]1~[#7:3]~[#7:4]~[#7:5]~[#6:6]~1>>[C:1][#7:2]1:[#7:3]:[#7:4]:[#7:5]:[#6:6]:1",
		"functional_groups": ["alcohol", "tetrazole_1"],
		"group_smarts": ["[C]~[#8;H1]", "[#7;H1]1~[#7]~[#7]~[#7]~[#6]~1"],
		"example_reactants": ["CC(O)C", "N1=NNC=N1"],
		"num_reactants": 2,
		"RXN_NUM": 37
	},
	"38_Mitsunobu_tetrazole_2": {
		"reaction_string": "[C:1][OH1][OH1].[#7H1:2]1~[#7:3]~[#7:4]~[#7:5]~[#6:6]~1>>[#7H0:2]1:[#7:3]:[#7H0:4]([C:1]):[#7:5]:[#6:6]:1",
		"functional_groups": ["alcohol", "tetrazole_1"],
		"group_smarts": ["[C]~[#8;H1]", "[#7;H1]1~[#7]~[#7]~[#7]~[#6]~1"],
		"example_reactants": ["CC(O)C", "N1=NNC=N1"],
		"num_reactants": 2,
		"RXN_NUM": 38
	},
	"39_Mitsunobu_tetrazole_3": {
		"reaction_string": "[C:1][OH1][OH1].[#7:2]1~[#7:3]~[#7H1:4]~[#7:5]~[#6:6]~1>>[C:1][#7H0:2]1:[#7:3]:[#7H0:4]:[#7:5]:[#6:6]:1",
		"functional_groups": ["alcohol", "tetrazole_2"],
		"group_smarts": ["[C]~[#8;H1]", "[#7]1~[#7]~[#7;H1]~[#7]~[#6]~1"],
		"example_reactants": ["CC(O)C", "N1N=NC=N1"],
		"num_reactants": 2,
		"RXN_NUM": 39
	},
	"40_Mitsunobu_tetrazole_4": {
		"reaction_string": "[C:1][OH1][OH1].[#7:2]1~[#7:3]~[#7H1:4]~[#7:5]~[#6:6]~1>>[#7:2]1:[#7:3]:[#7:4]([C:1]):[#7:5]:[#6:6]:1",
		"functional_groups": ["alcohol", "tetrazole_2"],
		"group_smarts": ["[C]~[#8;H1]", "[#7]1~[#7]~[#7;H1]~[#7]~[#6]~1"],
		"example_reactants": ["CC(O)C", "N1N=NC=N1"],
		"num_reactants": 2,
		"RXN_NUM": 40
	},
	"41_Heck_terminal_vinyl": {
		"reaction_string": "[#6;c,$(C(=O)O),$(C#N):3][#6;H1:2]=[#6;H2:1].[#6;$([#6]=[#6]),$(c:c):4][Cl,Br,I]>>[#6:4]/[#6:1]=[#6:2]/[#6:3]",
		"functional_groups": ["alkene", "halide"],
		"group_smarts": ["[#6;c,$(C(=O)O),$(C#N)][#6;H1]=[#6;H2]", "[#6][#6][Cl,Br,I]"],
		"example_reactants": ["c1ccccc1C=C", "c1ccccc1Br"],
		"num_reactants": 2,
		"RXN_NUM": 41
	},
	"42_Heck_non_terminal_vinyl": {
		"reaction_string": "[#6;c,$(C(=O)O),$(C#N):3][#6:2]([#6:5])=[#6;H1;$([#6][#6]):1].[#6;$([#6]=[#6]),$(c:c):4][Cl,Br,I]>>[#6:4][#6;H0:1]=[#6:2]([#6:5])[#6:3]",
		"functional_groups": ["terminal_alkene", "halide"],
		"group_smarts": ["[#6;c,$(C(=O)O),$(C#N)][#6]([#6])=[#6;H1;$([#6][#6])]", "[#6][#6][Cl,Br,I]"],
		"example_reactants": ["c1ccccc1C(C)=CC", "c1ccccc1Br"],
		"num_reactants": 2,
		"RXN_NUM": 42
	},
	"43_Stille": {
		"reaction_string": "[#6;$(C=C-[#6]),$(c:c):1][Br,I].[Cl,Br,I][a:2]>>[a:2][#6:1]",
		"functional_groups": ["aryl_or_vinyl_halide", "aryl_halide"],
		"group_smarts": ["[#6;$(C=C-[#6]),$(c:c)][Br,I]", "[Cl,Br,I][a]"],
		"example_reactants": ["c1ccccc1Br", "c1ccccc1Br"],
		"num_reactants": 2,
		"RXN_NUM": 43
	},
	"44_Grignard_carbonyl": {
		"reaction_string": "[#6:1][C:2]#[#7].[Cl,Br,I][#6;$([#6]~[#6]);!$([#6]([Cl,Br,I])[Cl,Br,I]);!$([#6]=O):3]>>[#6:1][C:2](=O)[#6:3]",
		"functional_groups": ["nitrile", "halide"],
		"group_smarts": ["[#6]#[#7]", "[#6][#6][Cl,Br,I]"],
		"example_reactants": ["CC#N", "CCBr"],
		"num_reactants": 2,
		"RXN_NUM": 44
	},
	"45_Grignard_alcohol": {
		"reaction_string": "[#6:1][#6:2]=[OD1:3].[Cl,Br,I][#6;$([#6]~[#6]);!$([#6]([Cl,Br,I])[Cl,Br,I]);!$([#6]=O):4]>>[C:1][#6:2]([OH1:3])[#6:4]",
		"functional_groups": ["aldehyde_or_ketone", "halide"],
		"group_smarts": ["[#6]-[C;R0]=[OD1]", "[#6][#6][Cl,Br,I]"],
		"example_reactants": ["CC(=O)C", "CCBr"],
		"num_reactants": 2,
		"RXN_NUM": 45
	},
	"46_Sonogashira": {
		"reaction_string": "[#6;$(C=C-[#6]),$(c:c):1][Br,I].[CH1;$(C#CC):2]>>[#6:1][C:2]",
		"functional_groups": ["aryl_or_vinyl_halide", "terminal_alkyne"],
		"group_smarts": ["[#6;$(C=C-[#6]),$(c:c)][Br,I]", "[CH1;$(C#CC)]"],
		"example_reactants": ["c1cc(Br)ccc1", "CC#C"],
		"num_reactants": 2,
		"RXN_NUM": 46
	},
	"47_Schotten_Baumann_amide": {
		"reaction_string": "[C;$(C=O):1][OH1].[#7;H1,H2:2]>>[C:1][N+0:2]",
		"functional_groups": ["carboxylic_acid", "primary_or_secondary_amine"],
		"group_smarts": ["[C;$(C=O)][OH1]", "[#7;H1,H2]"],
		"example_reactants": ["CC(=O)O", "NCC"],
		"num_reactants": 2,
		"RXN_NUM": 47
	},
	"48_sulfon_amide": {
		"reaction_string": "[#16:1](=[#8])(=[#8])(-[#8])[#6:2].[#7;H1,H2:3]>>[#6:2][#16:1](=[#8])(=[#8])[N+0:3]",
		"functional_groups": ["sulfonic_acid", "primary_or_secondary_amine"],
		"group_smarts": ["[#16](=[#8])(=[#8])(-[#8])[#6]", "[#7;H1,H2]"],
		"example_reactants": ["OS(=O)(=O)C", "NCC"],
		"num_reactants": 2,
		"RXN_NUM": 48
	},
	"49_N_arylation_heterocycles": {
		"reaction_string": "OB(O)[a:1].[n;H1,-;r5:2]>>[a:2]-[a:1]",
		"functional_groups": ["aryl_boronic_acid", "5_mem_aryl_w_NH_max2N"],
		"group_smarts": ["OB(O)c(a)a", "[a;r5:5][n;H1,-;r5:4]([a;r5:6])"],
		"example_reactants": ["c1ccccc1B(O)O", "N1C=NC=C1"],
		"num_reactants": 2,
		"RXN_NUM": 49
	},
	"50_Wittig": {
		"reaction_string": "[#6:3]-[#6:1]=[OD1].[Cl,Br,I][C;H2;$(C-[#6]);!$(CC[I,Br]);!$(CCO[CH3]):2]>>[C:3][C:1]=[C:2]",
		"functional_groups": ["aldehyde_or_ketone", "primary_or_secondary_halide"],
		"group_smarts": ["[#6]-[C;R0]=[OD1]", "[Cl,Br,I][C;H2;$(C-[#6]);!$(CC[I,Br]);!$(CCO[CH3])]"],
		"example_reactants": ["CC(=O)C", "BrCC"],
		"num_reactants": 2,
		"RXN_NUM": 50
	},
	"51_Buchwald_Hartwig": {
		"reaction_string": "[Cl,Br,I][a:1].[#7;H1,H2:2]>>[a:1][N:2]",
		"functional_groups": ["aryl_halide", "primary_or_secondary_amine"],
		"group_smarts": ["[Cl,Br,I][a]", "[#7;H1,H2]"],
		"example_reactants": ["c1ccccc1Br", "CNC"],
		"num_reactants": 2,
		"RXN_NUM": 51
	},
	"52_imidazole": {
		"reaction_string": "[#6:4](=[#8])[#6:5][Br].[#7;H2:3][C;$(C(=N)(N)[c,#7]):2]=[#7;H1;D1:1]>>[C:4]1=[CH0:5][NH:3][C:2]=[N:1]1",
		"functional_groups": ["alpha_halo_ketone", "amidine"],
		"group_smarts": ["[#6](=[#8])[#6][Br]", "[#7;H2][C;$(C(=N)(N)[c,#7])]=[#7;H1;D1]"],
		"example_reactants": ["CC(=O)C(Br)C", "N=C(N)NC"],
		"num_reactants": 2,
		"RXN_NUM": 52
	},
	"53_decarboxylative_coupling": {
		"reaction_string": "[c;$(c1ccccc1):1][C;$(C(=O)[O;H1])].[Cl,Br,I][a:2]>>[c:1][a:2]",
		"functional_groups": ["aryl_carboxylic_acid", "aryl_halide"],
		"group_smarts": ["[c;$(c1ccccc1)][C;$(C(=O)[O;H1])]", "[Cl,Br,I][a]"],
		"example_reactants": ["c1c(C(=O)O)c([N+](=O)[O-])ccc1", "c1ccccc1Br"],
		"num_reactants": 2,
		"RXN_NUM": 53
	},
	"54_heteroaromatic_nuc_sub": {
		"reaction_string": "[c;!$(c1ccccc1);$(c1[n,c]c[n,c]c[n,c]1):1][Cl,F].[#7;H1,H2:2]>>[c:1][N:2]",
		"functional_groups": ["pyridine_pyrimidine_triazine", "primary_or_secondary_amine"],
		"group_smarts": ["[c;!$(c1ccccc1);$(c1[n,c]c[n,c]c[n,c]1)][Cl,F]", "[#7;H1,H2]"],
		"example_reactants": ["c1cnc(F)cc1", "CN"],
		"num_reactants": 2,
		"RXN_NUM": 54
	},
	"55_nucl_sub_aromatic_ortho_nitro": {
		"reaction_string": "[c;$(c1c(N(~O)~O)cccc1):1][Cl,F].[#7;H1,H2:2]>>[c:1][N:2]",
		"functional_groups": ["ortho_halo_nitrobenzene", "primary_or_secondary_amine"],
		"group_smarts": ["[c;$(c1c(N(~O)~O)cccc1)][Cl,F]", "[#7;H1,H2]"],
		"example_reactants": ["c1c([N+](=O)[O-])c(F)ccc1", "CN"],
		"num_reactants": 2,
		"RXN_NUM": 55
	},
	"56_nucl_sub_aromatic_para_nitro": {
		"reaction_string": "[c;$(c1ccc(N(~O)~O)cc1):1][Cl,F].[#7;H1,H2:2]>>[c:1][N:2]",
		"functional_groups": ["para_halo_nitrobenzene", "primary_or_secondary_amine"],
		"group_smarts": ["[c;$(c1ccc(N(~O)~O)cc1)][Cl,F]", "[#7;H1,H2]"],
		"example_reactants": ["c1c(F)ccc([N+](=O)[O-])c1", "CN"],
		"num_reactants": 2,
		"RXN_NUM": 56
	},
	"57_urea": {
		"reaction_string": "[#7:3]=[#6:1]=[#8:4].[#7;H1,H2:2]>>[#7:3]-[C:1](=[#8:4])-[N+0:2]",
		"functional_groups": ["isocyanate", "primary_or_secondary_amine"],
		"group_smarts": ["[#7]=[#6]=[#8]", "[#7;H1,H2]"],
		"example_reactants": ["CN=C=O", "CN"],
		"num_reactants": 2,
		"RXN_NUM": 57
	},
	"58_thiourea": {
		"reaction_string": "[#7:3]=[#6:1]=[#16:4].[#7;H1,H2:2]>>[#7:3]-[C:1](=[#16:4])-[N+0:2]",
		"functional_groups": ["isothiocyanate", "primary_or_secondary_amine"],
		"group_smarts": ["[#7]=[#6]=[#16]", "[#7;H1,H2]"],
		"example_reactants": ["CN=C=S", "CN"],
		"num_reactants": 2,
		"RXN_NUM": 58
	}
}




def dothing(file):
    print(file)
    zinc_list = []
    smile_list = []

    with open(file,'r') as f:
        for line in f.readlines():
            line = line.replace("\n","")
            parts = line.split("\t")
            if len(parts) != 2:
                parts = line.split("    ")
                if len(parts) != 2:
                    raise Exception("Fail")
            smile = parts[0]
            zincID = parts[1]

            zinc_list.append(zincID)
            smile_list.append(smile)
       

    if len(smile_list)<50 or len(zinc_list)<50:
        raise Exception("FAIL NO LIGANDS!!!!!!!")
    print("Multithreading!!!!!")
    job_input = [[smile_list[i], zinc_list[i]] for i in range(0,len(smile_list))]
        
    output = mp.MultiThreading(job_input, -1,  dothing_to_mol)

    output = [x for x in output if x is not None]
    if len(output)==0:
        print("Finished Multithreading!!!!!")
        return None

    else:
        print("$$$$$$$$$$$$$$$$$$$$$")
        for i in output:
            if i==None:
                continue
            else:
                print(i)

    return file
    #
     
def dothing_to_mol(smile,zincID):       
    mol = Chem.MolFromSmiles(smile)
    mol = Chem.AddHs(mol) 
    Chem.SanitizeMol(mol)
    
    return [zincID, [smile,zincID, mol]]


def get_mols(file_name):

    job_input = [] 
    counter = 0
    with open(file_name,'r') as f:
        for line in f.readlines():
            line = line.replace("\n","")
            parts = line.split("\t")
            if len(parts) != 2:
                parts = line.split("    ")
                if len(parts) != 2:
                    raise Exception("Fail")
            counter = counter +1
            job_input.append((parts[0], parts[1]))
            continue
            
    # job_input = [[smile_list[i], zinc_list[i]] for i in range(0,len(smile_list))]
    output = mp.MultiThreading(job_input, -1,  dothing_to_mol)

    mol_dic = {}
    for x in output:
        mol_dic[x[0]] = x[1]

    return mol_dic

##############################
def conduct_reaction_one(mol_set, rxn, sub):
    mol = mol_set[2]

    if mol.HasSubstructMatch(sub) == False:
        mol = Chem.RemoveHs(mol)   
        if mol.HasSubstructMatch(sub) == False: 
            return False

    try:
        rxn.RunReactants((mol,))[0][0]
        return None
    except:
        return mol_set[0]

def conduct_reaction_two(mols_sets, rxn, subs):
    mol1 = mols_sets[0][2]
    mol2 = mols_sets[1][2]
    
    if mol1.HasSubstructMatch(subs[0]) == False:
        mol1 = Chem.RemoveHs(mol1)   
        if mol1.HasSubstructMatch(subs[0]) == False: 
            return False

    if mol2.HasSubstructMatch(subs[1]) == False:
        mol2 = Chem.RemoveHs(mol2)   
        if mol2.HasSubstructMatch(subs[1]) == False: 
            return False

    try:
        rxn.RunReactants((mol1,mol2))[0][0]
        return None
    except:
        return [mol1_set[0][0], mol2_set[1][0]]


if __name__ == "__main__":
    folder = "/mnt/data_1/DataB/jspiegel/projects/autogrow4/autogrow/Operators/Mutation/SmileClickChem/Reaction_libraries/Robust_Rxns/complimentary_mol_dir/"

    output_folder = "/home/jspiegel/DataB/jspiegel/FILTER_FOR_AUTO/pickled_lib/"
    list_files = [x for x in glob.glob(folder+"*.smi")]
    list_file_basename = [os.path.basename(x).replace(".smi","") for x in glob.glob(folder+"*.smi")]
    
    failed_files = []

    fun_Group_mols_dict = {}

    for name in list_file_basename:
        file_name = folder + name + ".smi"
        
        temp_pickle_name = output_folder + name+"_pickle"
        print(temp_pickle_name)
        if os.path.exists(temp_pickle_name)==True:
            print("     Already Exists")
        with open(temp_pickle_name, 'rb') as handle:
            mols_dict = pickle.load(handle)
            continue


        temp_mol = get_mols(file_name)


        with open(temp_pickle_name, 'wb') as handle:
            pickle.dump(temp_mol, handle, protocol=pickle.HIGHEST_PROTOCOL)
        fun_Group_mols_dict[name] = temp_pickle_name
        temp_mol= None
    print(fun_Group_mols_dict)
    import sys
    sys.exit(0)