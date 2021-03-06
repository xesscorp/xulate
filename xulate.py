import sys
import argparse
import re

"""Translate a UCF file with XuLA/XuLA2 pin loc constraints to those for a XuLA2/XuLA.

	This program accepts either a XuLA or XuLA2 UCF file and
	converts it to a XuLA2 or XuLA UCF file.

	xulate file.ucf
"""

# Table associating the XuLA pins to the XuLA2 pins.
xula_translate_tbl = (\
    ('p43', 'a9' ), # fpgaClk
    ('???', 'j12'), # sdCke
    ('p40', 'k11'), # sdClk
    ('p41', 'k12'), # sdClkFb
    ('???', 'h4' ), # sdCe
    ('p59', 'l4' ), # sdRas
    ('p60', 'l3' ), # sdCas
    ('p64', 'm3' ), # sdWe
    ('???', 'm4' ), #sdDqml
    ('???', 'l13'), #sdDqmh
    ('p53', 'h3' ), # sdBs0
    ('???', 'g3' ), # sdBs1
    ('p49', 'e4' ), # sdAddr<0>
    ('p48', 'e3' ), # sdAddr<1>
    ('p46', 'd3' ), # sdAddr<2>
    ('p31', 'c3' ), # sdAddr<3>
    ('p30', 'b12'), # sdAddr<4>
    ('p29', 'a12'), # sdAddr<5>
    ('p28', 'd12'), # sdAddr<6>
    ('p27', 'e12'), # sdAddr<7>
    ('p23', 'g16'), # sdAddr<8>
    ('p24', 'g12'), # sdAddr<9>
    ('p51', 'f4' ), # sdAddr<10>
    ('p25', 'g11'), # sdAddr<11>
    ('???', 'h13'), # sdAddr<12>
    ('p90', 'p6' ), # sdData<0>    
    ('p77', 't6' ), # sdData<1>    
    ('p78', 't5' ), # sdData<2>    
    ('p85', 'p5' ), # sdData<3>    
    ('p86', 'r5' ), # sdData<4>    
    ('p71', 'n5' ), # sdData<5>    
    ('p70', 'p4' ), # sdData<6>    
    ('p65', 'n4' ), # sdData<7>    
    ('p16', 'p12'), # sdData<8>    
    ('p15', 'r12'), # sdData<9>    
    ('p10', 't13'), # sdData<10>    
    ('p9' , 't14'), # sdData<11>    
    ('p6' , 'r14'), # sdData<12>    
    ('p5' , 't15'), # sdData<13>    
    ('p99', 't12'), # sdData<14>    
    ('p98', 'p11'), # sdData<15>    
    ('???', 't8' ), # usdFlashCs
    ('???', 't3' ), # flashCs
    ('???', 'r11'), # sclk
    ('???', 't10'), # mosi
    ('???', 'p10'), # miso
    ('p44', 't7' ), # chanClk   
    ('p36', 'r7' ), # chan<0>   
    ('p37', 'r15'), # chan<1>   
    ('p39', 'r16'), # chan<2>   
    ('p50', 'm15'), # chan<3>   
    ('p52', 'm16'), # chan<4>   
    ('p56', 'k15'), # chan<5>   
    ('p57', 'k16'), # chan<6>   
    ('p61', 'j16'), # chan<7>   
    ('p62', 'j14'), # chan<8>   
    ('p68', 'f15'), # chan<9>   
    ('p72', 'f16'), # chan<10>   
    ('p73', 'c16'), # chan<11>   
    ('p82', 'c15'), # chan<12>   
    ('p83', 'b16'), # chan<13>   
    ('p84', 'b15'), # chan<14>   
    ('p35', 't4' ), # chan<15>  
    ('p34', 'r2' ), # chan<16>  
    ('p33', 'r1' ), # chan<17>  
    ('p32', 'm2' ), # chan<18>  
    ('p21', 'm1' ), # chan<19>  
    ('p20', 'k3' ), # chan<20>  
    ('p19', 'j4' ), # chan<21>  
    ('p13', 'h1' ), # chan<22>  
    ('p12', 'h2' ), # chan<23>  
    ('p7' , 'f1' ), # chan<24>  
    ('p4' , 'f2' ), # chan<25>  
    ('p3' , 'e1' ), # chan<26>  
    ('p97', 'e2' ), # chan<27>  
    ('p94', 'c1' ), # chan<28>  
    ('p93', 'b1' ), # chan<29>
    ('p89', 'b2' ), # chan<30>
    ('p88', 'a2' ), # chan<31>
)

parser = argparse.ArgumentParser(description='Translate a XuLA UCF file to XuLA2.')
parser.add_argument('-infile', nargs='?', help='UCF file to convert', type=argparse.FileType('r'), default=sys.stdin)
parser.add_argument('-outfile', nargs='?', help='UCF file to hold conversion', type=argparse.FileType('w'), default=sys.stdout)
parser.add_argument('-iofile', nargs='?', help='UCF file to be converted in-place', )
args = parser.parse_args()

# Convert XuLA-XuLA2 pin association list into dictionaries.
xula_to_xula2_tbl = {}
xula2_to_xula_tbl = {}
for (xula_pin, xula2_pin) in xula_translate_tbl:
    # Create look-up table to convert XuLA pins to XuLA2 pins.
    if xula_pin != '???':
        if xula_pin.lower() in xula_to_xula2_tbl:
            raise Exception("Duplicate pin in XuLA table: " + xula_pin)
        xula_to_xula2_tbl[xula_pin.lower()] = xula2_pin.lower()
        xula_to_xula2_tbl[xula_pin.upper()] = xula2_pin.upper()
    # Create look-up table to convert XuLA2 pins to XuLA pins.
    if xula2_pin != '???':
        if xula2_pin.lower() in xula2_to_xula_tbl:
            raise Exception("Duplicate pin in XuLA2 table: " + xula2_pin)
        xula2_to_xula_tbl[xula2_pin.lower()] = xula_pin.lower()
        xula2_to_xula_tbl[xula2_pin.upper()] = xula_pin.upper()

# Get UCF file.
if args.iofile is not None:
    infile = open(args.iofile, 'r')
    ucf = infile.readlines()
    infile.close()
else:
    ucf = args.infile.readlines()

loc = r'(\s* loc \s* = \s*) (\w*) (\s* [;|])'
loc_re = re.compile(loc, re.IGNORECASE | re.VERBOSE)

# Determine if this is a XuLA or XuLA2 pin.
def pin_check( pin ):
    if pin in xula_to_xula2_tbl and pin not in xula2_to_xula_tbl:
        return 1, 0
    if pin in xula2_to_xula_tbl and pin not in xula_to_xula2_tbl:
        return 0, 1
    return 0, 0

# Determine if the input file contains XuLA or XuLA2 pin constraints.
xula_pin_cnt = 0
xula2_pin_cnt = 0
for line in ucf:
    m = loc_re.search(line)
    if m is not None:
        inc = pin_check(m.group(2))
        xula_pin_cnt += inc[0]
        xula2_pin_cnt += inc[1]
if xula_pin_cnt > xula2_pin_cnt:
    translate_tbl = xula_to_xula2_tbl
else:
    translate_tbl = xula2_to_xula_tbl
    
# Find lines containing "LOC = pin" and replace pin with a new value.
def pin_exchange( loc_line ):
    new_pin = translate_tbl[loc_line.group(2)]
    return loc_line.group(1) + new_pin + loc_line.group(3)

ucf = ''.join(ucf)    
new_ucf = loc_re.sub(pin_exchange, ucf)

# Store new UCF.
if args.iofile is not None:
    outfile = open(args.iofile, 'w')
    print >>outfile, new_ucf
    outfile.close()
else:
    print >>args.outfile, new_ucf
