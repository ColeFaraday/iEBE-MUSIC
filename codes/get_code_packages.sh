#!/usr/bin/env bash

# download the code package

# download 3DMCGlauber
rm -fr 3dMCGlauber_code
git clone https://github.com/chunshen1987/3dMCGlauber 3dMCGlauber_code
(cd 3dMCGlauber_code; git checkout 9af251c283e700a2abb9eb844a91da861136920f)
rm -fr 3dMCGlauber_code/.git

# download Cole's fork of IPGlasma
rm -fr ipglasma_code
git clone https://github.com/ColeFaraday/ipglasma ipglasma_code
(cd ipglasma_code; git checkout master) # can change to dev manually if needed
rm -fr ipglasma_code/.git

# download KoMPoST
rm -fr kompost_code
git clone https://github.com/chunshen1987/KoMPoST kompost_code
(cd kompost_code; git checkout 3a8f873bcf8e20ec8522cb851d20ae5e66610085)
rm -fr kompost_code/.git

# download MUSIC
rm -fr MUSIC_code
git clone https://github.com/MUSIC-fluid/MUSIC -b chun_dev MUSIC_code
(cd MUSIC_code; git checkout 062762b8a15b487259571f35517de9283af0a7ef)
rm -fr MUSIC_code/.git

# download iSS particle sampler
rm -fr iSS_code
git clone https://github.com/chunshen1987/iSS -b dev iSS_code
(cd iSS_code; git checkout 3b151fdd03f5cd0f41c19b11af68e379c4c5f571)
rm -fr iSS_code/.git

# download photonEmission wrapper
rm -fr photonEmission_hydroInterface_code
git clone https://github.com/chunshen1987/photonEmission_hydroInterface photonEmission_hydroInterface_code
(cd photonEmission_hydroInterface_code; git checkout 282397c2ca423886d806c755f120ea7b16572e03)
rm -fr photonEmission_hydroInterface_code/.git

# download UrQMD afterburner
rm -fr urqmd_code
git clone https://Chunshen1987@bitbucket.org/Chunshen1987/urqmd_afterburner.git urqmd_code
(cd urqmd_code; git checkout 704c886)
rm -fr urqmd_code/.git

# download hadronic afterner
rm -fr hadronic_afterburner_toolkit_code
git clone https://github.com/chunshen1987/hadronic_afterburner_toolkit hadronic_afterburner_toolkit_code
(cd hadronic_afterburner_toolkit_code; git checkout f78e71ee68a5cc12b7c1d856c34cc445410d64eb)
rm -fr hadronic_afterburner_toolkit_code/.git

