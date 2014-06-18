xulate
================================================================

This program accepts a XuLA or XuLA2 UCF file via the standard input and
converts the pin assignments to ones appropriate for the XuLA2 or XuLA.
The modified UCF is sent to the standard output:

	xulate < XuLA.ucf > XuLA2.ucf

You can also use arguments for the input and output UCF files:

	xulate -i XuLA2.ucf -o Xula.ucf
    
You can also convert a file in-place like so:

    xulate -iofile XuLA.ucf
