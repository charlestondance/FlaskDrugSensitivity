__author__ = 'Dovod'

import csv
import random

def make_hitlist(hitlist, copies, name):
    print(hitlist)
    print(copies)

    destination_wells_list = destination_wells()
    LAST_DEST_ITERATOR = 289

    intermediates = ["-I1", "-I2", "-I3", "-I4"]

    conc_a = [25.0, 2.5, 25.0, 2.5, 25.0]
    conc_b = [25.0, 7.5, 2.5, 25.0, 7.5]

    DMSO_WELLS = ['C3', 'H4', 'L4', 'F12', 'H12', 'L12', 'E17', 'J20']
    CONTROL_WELLS = ['E4', 'I7', 'E8', 'O8', 'C12', 'K16', 'B20', 'G20']

    DMSO_SOURCE = ["A1", "B1", "C1", "D1", "E1", "F1", "G1", "H1", "I1", "J1", "K1", "L1", "M1", "N1", "O1", "P1"]
    CONTROL_SOURCE = ["A24", "B24", "C24", "D24", "E24", "F24", "G24", "H24", "I24", "J24", "K24", "L24", "M24", "N24", "O24", "P24"]

    dest_barcode_letter = 'A'

    output_list = []
    #header
    header = ["Sample Name", "Source Plate Barcode", "Source Well", "Transfer Volume", "Destination Well", "Destination Plate Barcode"]
    output_list.append(header)

    for i in range(0, copies):
        destination_well_iterator = 0
        dest_barcode = 1

        for compound in hitlist:
            barcode_offset = 0
            barcodes_list = get_starting_barcode(compound[3], compound[1])
            volume_index = 0
            old_volume = 1000000.00

            #set the concentration range
            if compound[4] == "A":
                conc_list = conc_a
            else:
                conc_list = conc_b

            for volume_iterator in conc_list:

                get_volume = volume_iterator

                if old_volume > get_volume:

                    True
                else:
                    barcode_offset = barcode_offset + 1

                current_line_list = [compound[0], barcodes_list[barcode_offset], compound[2], volume_iterator, destination_wells_list[destination_well_iterator], name+"-"+dest_barcode_letter+str(dest_barcode)]

                output_list.append(current_line_list)

                destination_well_iterator = destination_well_iterator + 1

                #if got to the end of the available wells then reset everything and move onto the next barcode plate
                if destination_well_iterator == LAST_DEST_ITERATOR + 1:

                    destination_well_iterator = 0

                    dest_barcode = dest_barcode + 1

                old_volume = get_volume

        for i in range(dest_barcode):
            for dmso in DMSO_WELLS:
                    #print('FIXED' + ", " + 'DMSO' + ", " + DMSO_SOURCE + ", " + '20' + ", " + dmso + ", " + dest_barcode_letter + str(i+1))
                    current_line_list = ['DMSO', 'FIXED', DMSO_SOURCE[random.randint(0,15)], '25', dmso, name+"-"+dest_barcode_letter + str(i+1)]
                    output_list.append(current_line_list)
            for control in CONTROL_WELLS:
                    #print('FIXED' + ", " + 'Control' + ", " + CONTROL_SOURCE + ", " + '20' + ", " + control + ", " + dest_barcode_letter + str(i+1))
                    current_line_list = ['Control', 'FIXED', CONTROL_SOURCE[random.randint(0,15)], '25', control, name+"-"+dest_barcode_letter + str(i+1)]
                    output_list.append(current_line_list)
        #inrement the letter
        print(dest_barcode_letter)
        dest_barcode_letter = chr(ord(dest_barcode_letter) + 1)

    return output_list

def get_starting_barcode(starting_iterator, barcode):
    #return a list of the barcodes depending on starting value in DB
    intermediates = ["-I1", "-I2", "-I3", "-I4"]
    listofbarcode = []
    if int(starting_iterator) == 0:

        listofbarcode.append(barcode)
        for x in intermediates:
            listofbarcode.append(barcode + x)
        return listofbarcode
    else:
        for x in intermediates[int(starting_iterator):]:
            listofbarcode.append(barcode + x)
        return listofbarcode

def destination_wells():
    destination_wells = []
    with open('app/main/destination_wells.csv', newline='') as csvfile:
        read_source = csv.reader(csvfile, delimiter=',')
        for row in read_source:

            destination_wells.append(row[0])
    return destination_wells