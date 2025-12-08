<?xml version="1.0" encoding="UTF-8"?>
<dmodule xmlns:dc="http://www.purl.org/dc/elements/1.1/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://www.s1000d.org/S1000D_4-0/xml_schema_flat/descript.xsd">
	<rdf:Description>
		<dc:creator>IT-DEPT-09</dc:creator>
		<dc:title>Workstation - Hardware Assembly and Maintenance</dc:title>
		<dc:subject>Computer Hardware - Assembly Instructions</dc:subject>
		<dc:publisher>TechCorp</dc:publisher>
		<dc:contributor>TechCorp IT</dc:contributor>
		<dc:date>2024-03-15</dc:date>
		<dc:type>text</dc:type>
		<dc:format>text/xml</dc:format>
		<dc:identifier>S1000DPC-AAA-HW1-00-00-00AA-041A-A_000-00</dc:identifier>
		<dc:language>en-US</dc:language>
		<dc:rights>01_cc51_cv51</dc:rights>
	</rdf:Description>
	<identAndStatusSection>
		<dmAddress>
			<dmIdent>
				<dmCode assyCode="00" disassyCode="00" disassyCodeVariant="AA" infoCode="041" infoCodeVariant="A" itemLocationCode="A" modelIdentCode="S1000DPC" subSubSystemCode="0" subSystemCode="0" systemCode="HW1" systemDiffCode="AAA"/>
				<language countryIsoCode="US" languageIsoCode="en"/>
				<issueInfo inWork="00" issueNumber="001"/>
			</dmIdent>
			<dmAddressItems>
				<issueDate day="15" month="03" year="2024"/>
				<dmTitle>
					<techName>Workstation PC</techName>
					<infoName>Hardware Assembly and Maintenance</infoName>
				</dmTitle>
			</dmAddressItems>
		</dmAddress>
		<dmStatus issueType="new">
			<security securityClassification="01"/>
			<dataRestrictions>
				<restrictionInstructions>
					<dataDistribution>Internal distribution only.</dataDistribution>
					<exportControl>
						<exportRegistrationStmt>
							<simplePara>This data is not subject to export control. Standard company confidentiality applies.</simplePara>
						</exportRegistrationStmt>
					</exportControl>
					<dataHandling>Handle with care. ESD precautions required.</dataHandling>
					<dataDestruction>Standard paper shredding or digital wiping.</dataDestruction>
					<dataDisclosure>None.</dataDisclosure>
				</restrictionInstructions>
				<restrictionInfo>
					<copyright>
						<copyrightPara>
							<emphasis>Copyright (C) 2024</emphasis> by TechCorp Solutions.<randomList>
								<listItem>
									<para>TechCorp Hardware Division.</para>
								</listItem>
								<listItem>
									<para>Global IT Support Services.</para>
								</listItem>
							</randomList>
						</copyrightPara>
						<copyrightPara>
							<emphasis>Warranty Disclaimer:</emphasis>
						</copyrightPara>
						<copyrightPara>
							<randomList>
								<listItem>
									<para>Opening the power supply unit (PSU) voids all warranties immediately. High voltage capacitors present a lethal shock hazard even when unplugged.</para>
								</listItem>
								<listItem>
									<para>TechCorp is not liable for data loss resulting from improper hardware installation or static discharge damage.</para>
								</listItem>
								<listItem>
									<para>Ensure all data is backed up to the cloud or external storage before commencing any physical maintenance on the drive arrays.</para>
								</listItem>
							</randomList>
						</copyrightPara>
					</copyright>
					<policyStatement>IT-OPS-MAN-004</policyStatement>
					<dataConds>None.</dataConds>
				</restrictionInfo>
			</dataRestrictions>
			<responsiblePartnerCompany enterpriseCode="TC001">
				<enterpriseName>TechCorp</enterpriseName>
			</responsiblePartnerCompany>
			<originator enterpriseCode="TC001">
				<enterpriseName>TechCorp</enterpriseName>
			</originator>
			<applicCrossRefTableRef>
				<dmRef>
					<dmRefIdent>
						<dmCode assyCode="00" disassyCode="00" disassyCodeVariant="AA" infoCode="00W" infoCodeVariant="A" itemLocationCode="D" modelIdentCode="S1000DPC" subSubSystemCode="0" subSystemCode="0" systemCode="D00" systemDiffCode="AAA"/>
					</dmRefIdent>
				</dmRef>
			</applicCrossRefTableRef>
			<applic>
				<displayText>
					<simplePara>Enterprise Workstation Z-Series</simplePara>
				</displayText>
				<evaluate andOr="and">
					<assert applicPropertyIdent="model" applicPropertyType="prodattr" applicPropertyValues="Z-Series"/>
					<assert applicPropertyIdent="version" applicPropertyType="prodattr" applicPropertyValues="v4"/>
				</evaluate>
			</applic>
			<techStandard>
				<authorityInfoAndTp>
					<authorityInfo>20240315</authorityInfo>
					<techPubBase>PC Assembly Guide</techPubBase>
				</authorityInfoAndTp>
				<authorityExceptions/>
				<authorityNotes/>
			</techStandard>
			<brexDmRef>
				<dmRef>
					<dmRefIdent>
						<dmCode assyCode="00" disassyCode="00" disassyCodeVariant="AA" infoCode="022" infoCodeVariant="A" itemLocationCode="D" modelIdentCode="S1000DPC" subSubSystemCode="0" subSystemCode="0" systemCode="D00" systemDiffCode="AAA"/>
					</dmRefIdent>
				</dmRef>
			</brexDmRef>
			<qualityAssurance>
				<firstVerification verificationType="tabtop"/>
				<secondVerification verificationType="tabtop"/>
			</qualityAssurance>
			<systemBreakdownCode>HW10</systemBreakdownCode>
			<skillLevel skillLevelCode="sk02"/>
			<reasonForUpdate id="rfu-001" updateHighlight="0" updateReasonType="urt01">
				<simplePara>Initial Draft</simplePara>
			</reasonForUpdate>
		</dmStatus>
	</identAndStatusSection>
	<content>
		<description>
			<levelledPara>
				<title>Central Processing Unit (CPU)</title>
				<para>The Central Processing Unit (CPU) acts as the brain of the workstation. It executes instructions comprising a computer program. The CPU performs basic arithmetic, logic, controlling, and input/output (I/O) operations specified by the instructions in the program.</para>
				<para>Installation requires extreme care. The pins on the motherboard socket (LGA type) are extremely fragile. A single bent pin can render the entire motherboard inoperable. Ensure the retention arm is fully raised before attempting to place the processor into the socket.</para>
			</levelledPara>
			<levelledPara>
				<title>Thermal Management Systems</title>
				<para>High-performance workstations generate significant heat. The thermal solution typically involves a heatsink and fan assembly, or a liquid cooling loop. Thermal paste is applied between the CPU Integrated Heat Spreader (IHS) and the cold plate of the cooler to facilitate heat transfer.</para>
				<para>The efficiency of the cooling system depends on proper airflow within the chassis. Cable management is crucial to prevent air blockage. Fans should be oriented to create a push-pull configuration, drawing cool air in from the front and exhausting hot air out the rear.</para>
				<para>Periodic maintenance involves cleaning dust filters and checking fan bearings for noise. Accumulated dust acts as an insulator, causing component temperatures to rise and potentially leading to thermal throttling or hardware failure.</para>
			</levelledPara>
			<levelledPara>
				<title>Memory Modules (RAM)</title>
				<para>Random Access Memory (RAM) provides the high-speed workspace for the CPU. This workstation supports DDR5 ECC (Error Correction Code) memory, which is essential for data integrity in scientific and engineering applications. Unlike standard consumer memory, ECC RAM can detect and fix bit flips caused by cosmic radiation or electrical interference.</para>
				<para>Installation procedure requires ensuring the notch on the memory stick aligns with the key in the DIMM slot. Press down firmly until the locking tabs click into place. Do not force the module if it does not seat easily; check the alignment first.</para>
				<para>Common memory configurations include: <randomList listItemPrefix="pf02">
						<listItem>
							<para>32GB (2x 16GB) - Standard Office Use.</para>
						</listItem>
						<listItem>
							<para>64GB (4x 16GB) - Video Editing and Rendering.</para>
						</listItem>
						<listItem>
							<para>128GB (4x 32GB) - 3D Simulation and CAD.</para>
						</listItem>
						<listItem>
							<para>256GB (8x 32GB) - Server-grade Virtualization.</para>
						</listItem>
					</randomList>
				</para>
			</levelledPara>
			<levelledPara>
				<title>Storage Subsystem</title>
				<para>The storage subsystem utilizes NVMe solid-state drives (SSDs) connected directly to the PCIe bus for maximum throughput. Traditional SATA SSDs or HDDs may be used for bulk storage where speed is less critical. RAID configurations are supported for redundancy or performance.</para>
				<para>RAID 1 (Mirroring) writes data to two drives simultaneously, ensuring that if one drive fails, the data is preserved on the other. RAID 0 (Striping) splits data across drives for speed but offers no fault tolerance. RAID 5 combines speed and redundancy using parity bits.</para>
				<para>When installing M.2 NVMe drives, ensure the standoff screw is in the correct position for the length of the drive (typically 2280). Use the provided heatsink to prevent the controller from overheating during sustained write operations.</para>
			</levelledPara>
			<levelledPara>
				<title>Graphics Processing Unit (GPU)</title>
				<para>The GPU handles parallel processing tasks, primarily 3D rendering and video encoding. Modern workstations may employ multiple GPUs linked via a bridge for increased performance in specialized applications like machine learning or complex simulations.</para>
				<para>Power delivery is critical for high-end GPUs. Ensure that the dedicated PCIe power cables (6-pin, 8-pin, or 12VHPWR) are securely connected. Do not use daisy-chained splitters for cards exceeding 225W power draw, as this can overload the wires and cause voltage instability.</para>
				<para>Installation checklist: <randomList listItemPrefix="pf02">
						<listItem>
							<para>Remove the PCIe slot covers from the rear of the case.</para>
						</listItem>
						<listItem>
							<para>Unlock the PCIe retention clip on the motherboard slot.</para>
						</listItem>
						<listItem>
							<para>Align the card gold contacts with the slot and press down evenly.</para>
						</listItem>
						<listItem>
							<para>Secure the card bracket to the chassis using thumbscrews.</para>
						</listItem>
						<listItem>
							<para>Connect the necessary power cables from the PSU.</para>
						</listItem>
					</randomList>
				</para>
			</levelledPara>
			<levelledPara>
				<title>Power Supply Unit (PSU)</title>
				<para>The Power Supply Unit converts high voltage AC wall power into stable DC voltages (12V, 5V, 3.3V) used by the computer components. It is the most critical component for system stability. A failing PSU can damage every other component in the system.</para>
				<para>Efficiency ratings (80 Plus Bronze, Gold, Platinum, Titanium) indicate how much power is wasted as heat during conversion. A higher rating means less heat and lower electricity bills over time. For this workstation, an 80 Plus Gold unit is the minimum standard.</para>
				<para>Modular PSUs allow cables to be attached only as needed, reducing clutter and improving airflow. When adding cables, ensure they are the original cables supplied with the unit. Cables from different PSU manufacturers (or even different series from the same manufacturer) are often pin-incompatible and can cause immediate catastrophic failure.</para>
			</levelledPara>
			<levelledPara>
				<title>Troubleshooting Boot Failures</title>
				<para>If the system fails to boot (POST), observe the diagnostic LEDs or 7-segment display on the motherboard. These indicators provide error codes that can help isolate the faulty component (CPU, DRAM, VGA, BOOT).</para>
				<para>Common error codes and solutions: <randomList listItemPrefix="pf02">
						<listItem>
							<para>Code 55: Memory not installed. Reseat RAM modules.</para>
						</listItem>
						<listItem>
							<para>Code 99: Super IO Initialization. Check USB devices.</para>
						</listItem>
						<listItem>
							<para>Code A2: IDE Detect. Check SATA/NVMe connections.</para>
						</listItem>
						<listItem>
							<para>Code 00: CPU not detected. Check CPU socket pins or PSU power.</para>
						</listItem>
					</randomList>
				</para>
				<para>If no display appears, try resetting the CMOS (Complementary Metal-Oxide-Semiconductor) memory. This clears the BIOS settings to factory defaults. This can be done by removing the coin cell battery for 30 seconds or using the clear CMOS jumper/button.</para>
			</levelledPara>
		</description>
	</content>
</dmodule>
