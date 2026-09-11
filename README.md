# SpaceX SBC PCB Design by Austin Driggs


## INTRODUCTION

This repository contains the complete PCB architecture and design process for a custom Single Board Computer (SBC), prepared for a technical interview presentation for a PCB Design Engineer at SpaceX before I graduated from WVU. It walks through component package selection, power budget calculations, SoC and DDR3 memory constraint analysis, and 8-layer stackup optimization.

> **Disclaimer:** This project is an independent personal design exercise created solely for educational and portfolio demonstration purposes. It is not affiliated with, endorsed by, sponsored by, or associated with Space Exploration Technologies Corp. (SpaceX). All trademarks, logos, and brand names mentioned herein belong to their respective owners.


## PRESENTATION

### Prompt

- You are working with a design engineer on a small computer board.
- The computer board has a SoC, DDR3 DRAM, NAND flash, DC input that is converted to 5V and 3.3V using an onboard DC/DC converter, I/O circuits, etc.
- The SoC is available in BGA, QFN, QFP, bare die. The package outline varies between 8mm x 8mm to 40mm x 40mm depending on the ball/pin pitch which varies between 0.4mm to 1.0mm
- The NAND flash is available in BGA, QFN, and QFP
- The SoC consumes 5W, the DRAM 1W, the NAND flash 0.5W
- You have to help the engineer define the board size, component placement, component selection because the components come in different sizes, footprints, etc, select the board stack up and board technology. 

![Prompt Diagram](attachments/image-20260414125854%203.png)


### Personal Notes

26 pin rpi GPIO: ![RPi GPIO Diagram](attachments/image-20260414125854%204.png)

The DDR3 DRAM x16 is a single IC, so we won't need Fly-By-Topology (for addr and clk) and the extra layout space that two x8 ICs would take up.
Also assuming DDR3 and not DDR3L since that's what the block diagram is. DDR3 uses standard operating voltage of 1.5V (instead of L of 1.25V).
Also assuming that since its DDR3, it has On-Die-Termination (ODT) for the resistors.
![DDR3 Notes](attachments/image-20260414125854%205.png)

NAND Flash: can be 8 or 16 bit. For 8 bit, you can use the same IC but NC D8-D15. `Note:  Booting on 16-bit NAND Flash is not possible; only 8-bit NAND Flash memories are supported.`
![NAND Flash Notes](attachments/image-20260414125854%206.png)

What is RS232? [The RS-232 protocol](https://youtu.be/AHYNxpqKqwo?si=b2U9MRt10fqlJJua) by [Ben Eater](https://www.youtube.com/@BenEater).

Power supplies:
- 3.3V and 5V required
	- uP 5W/3.3V = 1.515A -> 3-5 A supply
- 1.8V for NAND Flash
	- 0.5W = 0.278A -> 0.5A supply 
- 1.5V (really 1.35V) for DDR3(L) and for the uP
	- DRAM 1W = 0.667A -> 2A
- 3.3V is Vdd for the uP
- 1.25V is Vcore for the uP 
- Summary:
- 5V @ 3A
- 3.3V @ 3A

https://www.digikey.com/en/products/detail/texas-instruments/TPS5430DDA/968136

![Power Supply Schematic 1](attachments/image-20260414125854%207.png)
![Power Supply Schematic 2](attachments/image-20260414125854%208.png)



### Questions for the Engineer

Higher Priority:
1. Are there any monetary constraints for the parts or for the manufacturing process?
2. Are there any mechanical or enclosure contraints? Do the IO and power connectors or mounts have to go in a specific location?
3. Are there any environmental constraints: space, thermal relief, EMC/EMI requirements?
4. What type of processing power does the board require? What's the target speed for the SoC and DDR3 DRAM?
5. Is there a specific processor family or architecture required for the project?
6. The voltage input is flexible (8V to 30V), but will the power be constant?
7. Can the board be double sided? At least having smaller/thinner components on the bottom.

Higher Affects:
1. BGA pitch, number of layers, via sizes, trace widths, surface finish, dialectric material.
2. Component spacing, ease of routing, total board size, height limitations.
3. External heatsink for the SoC, enclosure grounding, or shielding.
4. Stackup (layer heights and dialectric material), impedance control, length matching/tuning.
5. Limits package availability, power sequencing complexity, peripheral devices, and the software development stack.
6. If the input current is limited to 1A max, it could result in a 22W difference from 8-30V.
7. BGA SoC need capacitors on the directly under the IC to keep them as close as possible to the power pins.

Lower Priority:
1. How is power being input? Does there need to be any protection?
2. What voltage level are the IO circuits (both Analog and Digital)? How are we interfacing with them?
3. How much current will the IO circuits draw? Both the ICs that the SoC connects to and the devices that will connect to the MX34 and Pi headers.
4. How many GB is needed for the DDR3 DRAM? And what configuration?
5. What size and type of NAND Flash is required (by the engineer or the SoC)?


Lower Affects:
1. Input filters, reverse-polarity protection, fusing, PMICs.
2. Logic level shifters, buffers, communication protocols, or any other ICs required between the SoC and the MX34.
3. DC/DC converter selection, copper weight, thermals, PMIC or protection.
4. Routing density and number of address pins required. One x16 vs two x8's.
5. Routing desnity: SPI (fewer pins) vs (more pins) Parallel NAND and their packages.


### Assumptions I've Made

To move the design process along, I made the following assumptions:
1. I could make reasonable upgrades to component technology as long as there wasn't a drastic price difference.
2. Additional regulators: DDR3 requires a +1V5 voltage source (or +1V35 for DDR3L), so we will at least need to add a +1V5 regulator, as well as any additional voltages for the SoC. I would also assume the NAND flash is +1V8.
3. I will calculate the wattage required for each voltage level and then double it for a factor of safety. I would use buck converters for the main voltage levels (+5V and +3V3) and LDO's when applicable. 
4. For a basic SBC with DDR3 speeds (~800 MHz) and relatively short traces, FR4 will be acceptable.
5. I will try to use standard vendor technologies and materials where applicable: trace widths, through hole vias, stackup heights.

### Initial SoC Pin Calculations

Count the number of pins needed:
- DDR3 DRAM x16 = ~50 signal pins
- NAND Flash = ~15 signal pins (for 8-bit flash)
- Raspberry Pi Header = 17 signal pins
- RTC = 2 signal pins
- RS232 and Serial TTL = ~10 signal pins
- CAN Transciever = ~4 signal pins
- Digital and Analog <= 21 signal pins
- Total signal pin estimate = 119

Total number of pins required:
- Total signal pins / estimated 60% of pins are signals = 198.3 total pins
- Due to the significant number of pins and speed of DDR3, I already am thinking that a BGA package would be the best solution for the SoC.
- BGA's are also the most popular package for SoC, allowing for the widest variety of SoC options.

### Initial Power Calculations

Calculate the current output for each power supply:
- If the SoC consumed all +5V: 5W / +5V = 1A.
- +5V at 3A would be sufficent to power the entire board.
- If the SoC consumed all +3V3: 5W / +3V3 = 1.5A.
- +3V3 at 3A would be sufficent to power the entire board.
- NAND: 0.5W / +1V8 = 0.278A -> 0.5A to 1A supply would be sufficient.
- DDR3: 1W / +1V5 = 0.667A -> 1A to 2A supply would be sufficient.

Summary of calculated values:

| Vin   | Vout | Iout | Pout | Regulator      | Pdiss |
| ----- | ---- | ---- | ---- | -------------- | ----- |
| 8-30V | +5V  | 3A   | 15W  | Buck (90% eff) | 1.67W |
| 8-30V | +3V3 | 3A   | 9.9W | Buck (90% eff) | 1.10W |
| +3V3  | +1V8 | 1A   | 1.8W | LDO            | 1.50W |
| +3V3  | +1V5 | 1A   | 1.5W | LDO            | 1.80W |

Maximum amount of input current would be around 5A for the lowest 8V input.

### SoC Research

Inital package research:
- I rounded to 196 total pins which is a common 14x14 BGA package.
- I looked at some other packages, such as 200+ pin QFP or BGA options.
- I also did try to make sure the SoCs I looked at were able to meet every project requirement.

Package analysis:
- I would not use a bare die because of the manufacturing complexity and cost, environmental risks, and a cost vs benifits analysis.
- Standard (single-row) QFN packages max out at around 100 pins. Multi-row QFN do exist, but are less popular.
- QFP packages that are ~200 pins would fit the 40x40mm size constraint, but usually have a small pitch and take up significantly more space than a BGA package.

### SoC Research (image)

![SoC Research](attachments/image-20260414125854%209.png)

### SoC Package Selection

- Since I don't need that many pins, and I'm not too constained on size, I would rather have the larger-pitched and better performance BGA over the smaller-pitched QFP.  (Assuming double sided for BGA capacitors)
- I decided to go with a BGA 11x11mm SoC that had 0.75mm pitch, resulting in a 14x14 grid with 196 total pins, represented by the Microchip SAMA5D. 
- I'm using it to verify and prove my decisions throughout the rest of this presentation, but if this was purely theoretical, I would use either 0.8mm or 1mm pitch as they are more common and make both engineering and manufacturing easier.

A few benefits include:
- BGA has less parasitic inductance compared to QFP.
- BGA has superior thermal management.
- 196 pin BGA only requires around 2-3 signal layers to fan out.
- The relatively large pitch allows plenty of room for vias and dog-bones.

A few drawbacks include:
- BGA's are harder to rework and would require an X-ray to for inspection and QA.
- By choosing exactly the number of pins that I estimated, it doesn't leave much room for flexibility if the board requirements increased.


### SoC Analysis

Right now, I'm thinking that the overall board size will be between 50x50mm and 100x100mm, and I'll keep that in mind when picking out the remaining components.
- I know that I'll have to supply power, have room for the larger MX34 and RPI headers, and all the IO peripherals.
- The SoC will have the DDR, Flash, and RTC close to it.
- The IO peripherals will go between the SoC and the MX34. 
- The regulators will go further away from critical high-speed components.

Next Steps: Focus on designing each 'section' of components, and then combining them on one board.


### SoC Peripherals

- I would use 0201 caps underneath and as close as possible to every power pin.
- I would use larger decoupling capacitors as needed and as recommended by the manufacturerer and datasheet.
- I would leave enough clearence around the SoC to properly fanout all the signals.
- I would also leave room for mounting holes if an external heat sink was required, especially if the SoC consuming 5W.

![SoC Peripherals Layout](attachments/image-20260414125854%2010.png)

### DDR3 DRAM x16

- After selecting the SoC, I would look through its datasheet to see if it has prefered components for its memory.
- BGA packages are also the most popular for DDR memory due to the pin density and speed required.
- In this case, the SAMA5D recommends using a **96 pin BGA that's 8x14mm with 0.8mm pitch**.
- This pin layout and pitch aligns well with the SoC pitch, allowing for dogbone vias and enough room to fanout traces.

![DDR3 DRAM Footprint](attachments/image-20260414125854%2011.png)

> MT41K256M16TW
> 32M x 16-bit x 8 Banks (4-Gbit / 512 MB) DDR3L SDRAM, 1.35V nominal supply voltage, Rev. P, FBGA-96 (8x14mm)
> Package_BGA:Micron_FBGA-96_8x14mm_Layout9x16_P0.8mm

### NAND Flash

- I would follow the same process for the NAND Flash, assuming that I wanted to use parallel NAND.
- The datasheet for the SoC also recommended a 63 pin VFBGA  that's 9x11mm with 0.8mm pitch.
- While TSOP is another popular package, this BGA pin layout and pitch aligns well with the SoC, resulting in about the same requirements for manufacturing (via and trace sizes, room to fanout, etc).

![NAND Flash Footprint](attachments/image-20260414125854%2012.png)

> MT29F2G08ABDHC
> FLASH - NAND Memory IC 2Gbit Parallel 63-VFBGA (10.5x13)
> Package_BGA:BGA-63_9x11mm_Layout10x12_P0.8mm

### Power Input and Regulation

Referencing the table I made earlier, I would search both Digikey/Mouser and the SoC datasheet for appropriate power supplies. For this demo, I decided on the following:
- +5V and +3V3: TI TPS5430DDA adjustable buck switching regulator with 3A continuous output in an 8-PowerSOIC package.
- SOIC are a popular choice for this, and the large ground pad benifits thermals and efficiency.
- SoC/DDR/NAND Voltages: Microchip MCP16501 PMIC that outputs all other required voltages, at 1A each, and in a small QFN-24 4x4mm package with 0.5mm pitch and 2.7x2.7mm EP.
- The input connector is a Molex Microfit+, which is capable of over 10A of input current.

![Power Regulation Diagram](attachments/image-20260414125854%2013.png)

### CAN, RS232, and RTC

- Since this is a generic SBC, I would pick out the rest of the parts based on what's popular, what I've used before and is easy to assemble, and what we commonly use here or already have in stock.
- I would also try to balance the cost of the component, size, and complexity compared to the requirement. 
- I ended up going with the following:
	- CAN: Microchip MCP2562 in a SOIC-8 3.9 x 4.9 mm package with 1.27mm pitch.
	- RS232: TI MAX3221 in a SSOP-16 4.4 x 5.2 mm package with 0.65mm pitch.
	- RTC: SOIC-8 or DFN-8 if an external RTC is required. Some have built in crystals.
	- XTAL: Standard 4-pin SMD 2.5 x 2.0 mm package at 32.768 kHz.

### Digital Output Drivers and Analog Input Conditioning

- I wasn't entirely sure what to do with the digital and analog sections, so I've left plenty of room for placeholder ICs. I would need more information from the engineer.
- For verifying the 196-pin SoC, I created 8 spare signals for the digital output driver and 13 for the analog input conditioning.
- Possibilities include: logic level shifters, buffers, communication protocols, or any other ICs required between the SoC and the MX34.
- The biggest contributing factor is how much current that these signals would be driving, and if that current had to be supplied from one of the onboard regulators to an MX34 power pin.
- The MX34 is rated for 3A per pin, but hopefully we won't reach that.

![IO Drivers and Conditioning](attachments/image-20260414125854%2014.png)

### Stackup Layer Selection: 6-Layer

- Based off of the SoC and other selected components, I wanted to try a 6-layer stackup.
- The main contributing factor is the SoC BGA fanout and the DDR3 impedance.
- I would use a prefered vendor and select their standard 6-layer stackup and board height.

1. Signal: Main fanout for the SoC and other BGA components. Optional routing of power.
2. GND: Standard un-split ground plane.
3. Signal: Stripline layer for the DDR3 and other higher-speed signals.
4. Power: Split power planes for all voltage levels, especially for the SoC.
5. GND: Standard un-split ground plane.
6. Signal: Main fanout for the SoC and other BGA components. Optional routing of power.

![6-Layer Stackup Selection](attachments/image-20260414125854%2015.png)

> https://www.sunstone.com/docs/default-source/layer-stack-up-2022/l06-062-1-hv2.pdf

%% Standard trace width rules use 10 mils per amp for outer layers and 20 mils per amp for inner layers, assuming 1 oz copper. %%

### Stackup Layer Calculations: 6-layer

However, I started calculating and the trace widths needed to be larger than what was possible, especially on the outer layers.

![6-Layer Calculations 1](attachments/image-20260414125854%2016.png)

![6-Layer Calculations 2](attachments/image-20260414125854%2017.png)

### Stackup Alternatives

Even making the board thinner (1.0mm) and going up to 8 layers did not help routing DDR3 on the outer layers.

![Stackup Alternatives 1](attachments/image-20260414125854%2018.png)
![Stackup Alternatives 2](attachments/image-20260414125854%2019.png)


### Stackup Layer Selection: 8-Layer

1. Signal: Mixed signal
2. GND
3. Signal: High-speed DDR3
4. Power: Mainly SoC
5. GND
6. Signal: High-speed DDR3
7. GND
8. Signal: Mixed signal

![8-Layer Stackup Selection](attachments/image-20260414125854%2020.png)


### Stackup Layer Analysis: 8-Layer

Moving to an 8-layer board has many benefits:
- The dual stripline routing helps eliminate EMI and external noise.
- Reduced cross-talk as there's more space for signals to be routed.
- Easier length matching since there's more room.
- Better thermal performance across the board.
- Reduced thermal warpage and better layer symmetry.

Drawbacks:
- Costs more.

### Stackup Layer Calculations: 8-Layer for Sunstone Circuits

![8-Layer Calculations Sunstone 1](attachments/image-20260414125854%2021.png)
![8-Layer Calculations Sunstone 2](attachments/image-20260414125854%2022.png)

### Stackup Layer Calculations: 8-Layer for JLCPCB

![8-Layer Calculations JLCPCB](attachments/image-20260414125854%2023.png)

### Block Diagram Layout

![Block Diagram Layout](attachments/image-20260414125854%2024.png)

### Optimizing Component Placement

- I assigned net labels to the different signals and color-coded them.

![Component Placement Net Labels](attachments/image-20260414125854%2027.png)

At this point, I would verify this layout and 3D model with any mechanical engineers.

### Routing Power

![Power Routing](attachments/image-20260414125854%2030.png)

### Routing Signals

- I moved pins around inside of the schematic (assuming that all GPIO were able to have most functionalities).

![Signal Routing](attachments/image-20260414125854%2033.png)

### Cost Analysis

Inputs:
- Quantity: 10
- Advanced PCB/PCBA
- 8 layers, 75x75mm
- 1.6mm thickness
- HASL Finish, FR4 TG170
- 1oz copper layers
- Impedance controlled
- Min hole size = 0.2mm
- Stackup: JLC081611-3313

![Cost Analysis 1](attachments/image-20260414125854%2034.png)

![Cost Analysis 2](attachments/image-20260414125854%2035.png)

Total = $259.34 for 10 boards = $25.93 per board.


## CONCLUSION

- You are working with a design engineer on a small computer board.
- The computer board has a SoC, DDR3 DRAM, NAND flash, DC input that is converted to 5V and 3.3V using an onboard DC/DC converter, I/O circuits, etc.
- The SoC is available in BGA, QFN, QFP, bare die. The package outline varies between 8mm x 8mm to 40mm x 40mm depending on the ball/pin pitch which varies between 0.4mm to 1.0mm
- The NAND flash is available in BGA, QFN, and QFP
- The SoC consumes 5W, the DRAM 1W, the NAND flash 0.5W
- You have to help the engineer define the board size, component placement, component selection because the components come in different sizes, footprints, etc, select the board stack up and board technology. 

- Started with asking questions, defining requirements, and establising assumptions.
- Calculations for power, number of SoC pins, and trace impedance values.
- Researched, analyzed, and selected a SoC package.
- Selected SoC peripherals including the DRAM, Flash, and RTC.
- Determined types and ratings for the voltage regulators.
- Designed the stackup, technology, and component placement.

![Final Board Summary](attachments/image-20260414125854%2037.png)

