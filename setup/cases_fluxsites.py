#
## Met files ...
#
# met_subset = ['FI-Hyy_1996-2014_FLUXNET2015_Met.nc',\
#              'AU-Tum_2002-2017_OzFlux_Met.nc']
# met_subset = ['TumbaFluxnet.1.4_met.nc']

# Till fixed
# met_dir = "/g/data/w35/mgk576/research/CABLE_runs/met/Ozflux"
# met_subset = ["AU-Tum_2002-2017_OzFlux_Met.nc", "AU-How_2003-2017_OzFlux_Met.nc"]
met_subset = []  # if empty...run all the files in the met_dir


#
## science configs
#
sci1 = {
    "cable_user%GS_SWITCH": "'medlyn'",
}

sci2 = {
    "cable_user%GS_SWITCH": "'leuning'",
}

sci3 = {
    "cable_user%FWSOIL_SWITCH": "'Haverd2013'",
}

sci4 = {
    "cable_user%FWSOIL_SWITCH": "'standard'",
}

sci5 = {
    "cable_user%GS_SWITCH": "'medlyn'",
    "cable_user%FWSOIL_SWITCH": "'Haverd2013'",
}

sci6 = {
    "cable_user%GS_SWITCH": "'leuning'",
    "cable_user%FWSOIL_SWITCH": "'Haverd2013'",
}


sci7 = {
    "cable_user%GS_SWITCH": "'medlyn'",
    "cable_user%FWSOIL_SWITCH": "'standard'",
}

sci8 = {
    "cable_user%GS_SWITCH": "'leuning'",
    "cable_user%FWSOIL_SWITCH": "'standard'",
}


# sci_configs = [sci1, sci2, sci3, sci4, sci5, sci6, sci7, sci8]
sci_configs = [sci1]
