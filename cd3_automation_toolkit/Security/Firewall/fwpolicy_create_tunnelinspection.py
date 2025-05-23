#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# firewall, Listeners
#
# Author: Suruchi Singla
# Oracle Consulting
#
from oci.config import DEFAULT_LOCATION
from pathlib import Path
from commonTools import *
from jinja2 import Environment, FileSystemLoader
import os

######
# Required Inputs-CD3 excel file, Config file AND outdir
######

# Execution of the code begins here
def fwpolicy_create_tunnelinspect(inputfile, outdir, service_dir, prefix, ct):
    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True)
    tunnelinspect = env.get_template('policy-tunnelinspect-template')


    sheetName = "Firewall-Policy-TunnelInspect"
    tunnelinspect_auto_tfvars_filename = prefix + "_"+sheetName.lower()+".auto.tfvars"

    filename = inputfile

    outfile = {}
    oname = {}
    tunnelinspect_str = {}
    tunnelinspect_names = {}


    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)

    df = df.dropna(how='all')
    df = df.reset_index(drop=True)


    for reg in ct.all_regions:
        tunnelinspect_str[reg] = ''
        tunnelinspect_names[reg] = []
        reg_out_dir = outdir + "/" + reg + "/" + service_dir
        resource = sheetName.lower()
        commonTools.backup_file(reg_out_dir, resource, tunnelinspect_auto_tfvars_filename)


    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    region_seen_so_far = []
    region_list = []

    for i in df.index:
        region = str(df.loc[i, 'Region'])
        region = region.strip().lower()
        if region.lower() != 'nan' and region in ct.all_regions:
            region = region.strip().lower()
            if region not in region_seen_so_far:
                region_list.append(region)
                region_seen_so_far.append(region)
        if region in commonTools.endNames:
            break
        if region != 'nan' and region not in ct.all_regions:
            print("\nInvalid Region; It should be one of the regions tenancy is subscribed to...Exiting!!")
            exit()




        # temporary dictionaries
        tempStr= {}
        tempdict= {}
        dst_id = ''
        src_id = ''



        # Fetch data; loop through columns
        for columnname in dfcolumns:

            # Column value
            columnvalue = str(df[columnname][i]).strip()

            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue,columnname,tempdict)


            if columnname == "Firewall Policy":
                policy_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'policy_tf_name': policy_tf_name}

            if columnname == "Rule Name":
                rule_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'rule_tf_name': rule_tf_name,'rule_name':columnvalue}

            if columnname == "Source Address":
                if columnvalue != '':
                    srcaddrs = str(columnvalue).strip().split(",")
                    if len(srcaddrs) == 1:
                        for src in srcaddrs:
                            src_id = "\"" + src.strip() + "\""

                    elif len(srcaddrs) >= 2:
                        c = 1
                        for src in srcaddrs:
                            data = "\"" + src.strip() + "\""

                            if c == len(srcaddrs):
                                src_id = src_id + data
                            else:
                                src_id = src_id + data + ","
                            c += 1
                    columnvalue = src_id
                    tempdict = {'src_address': src_id}

            if columnname == "Destination Address":
                if columnvalue != '':
                    dstaddrs = str(columnvalue).strip().split(",")
                    if len(dstaddrs) == 1:
                        for dst in dstaddrs:
                            dst_id = "\"" + dst.strip() + "\""

                    elif len(dstaddrs) >= 2:
                        c = 1
                        for dst in dstaddrs:
                            data = "\"" + dst.strip() + "\""

                            if c == len(dstaddrs):
                                dst_id = dst_id + data
                            else:
                                dst_id = dst_id + data + ","
                            c += 1
                    columnvalue = dst_id
                    tempdict = {'dst_address': dst_id}


            if columnname == "Action":
                tempdict = {'action': columnvalue}

            if columnname == "Position":
                if columnvalue != '':
                    position = str(columnvalue).strip().split("::")
                    placement = position[0]
                    rule_place = position[1]
                    tempdict = {'placement': placement, 'rule_place': rule_place}

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)


        tunnelinspect_str[region] = tunnelinspect_str[region] + tunnelinspect.render(tempStr)

    for reg in region_list:
        reg_out_dir = outdir + "/" + reg + "/" + service_dir
        if not os.path.exists(reg_out_dir):
            os.makedirs(reg_out_dir)
        outfile[reg] = reg_out_dir + "/" + tunnelinspect_auto_tfvars_filename
        if tunnelinspect_str[reg] != '':
            # Generate Final String
            src = "##Add New Tunnel inspection rules for " + reg.lower() + " here##"
            tunnelinspect_str[reg] = tunnelinspect.render(count=0, region=reg).replace(src, tunnelinspect_str[reg] + "\n" + src)
            tunnelinspect_str[reg] = "".join([s for s in tunnelinspect_str[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            tunnelinspect_str[reg] = "\n\n" + tunnelinspect_str[reg]
            oname[reg] = open(outfile[reg], 'a')
            oname[reg].write(tunnelinspect_str[reg])
            oname[reg].close()
            print(outfile[reg] + " containing TF for Firewall Policy tunnel inspection rules has been updated for region " + reg)
