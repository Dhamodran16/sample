# XML to PDF with Java and Apache FOP (Manual Setup)

This project demonstrates how to convert XML files to PDF using Apache FOP (Formatting Objects Processor) with a simple Java setup, without Maven, Gradle, or Spring.

## Prerequisites

- **Java JDK**: Install Java (at least JDK 8; Apache FOP requires "Java 1.4 or later"). Ensure `javac` and `java` are on your PATH.
- **Apache FOP**: Download the latest binary distribution from [Apache FOP Downloads](https://xmlgraphics.apache.org/fop/download.html). Look for the "-bin" package (e.g., `fop-2.11-bin.zip`).

## Project Structure

```
my-project/
├── lib/          (Apache FOP JAR files - to be populated)
├── src/          (Java source code and XML/XSL files)
│   ├── XmlToPdf.java
│   ├── data.xml
│   └── template.xsl
└── out/          (compiled classes and output PDF)
```

## Setup Instructions

### 1. Download and Extract Apache FOP

1. Download the latest FOP binary distribution from the [Apache FOP website](https://xmlgraphics.apache.org/fop/download.html)
2. Extract the ZIP file to a convenient location
3. Navigate to the extracted FOP directory and locate the `lib/` folder

### 2. Copy JAR Files to Project

Copy all JAR files from the FOP distribution's `lib/` folder to this project's `lib/` directory. Required JARs typically include:

- `fop.jar`
- `xmlgraphics-commons-*.jar`
- `batik-*.jar` (or `batik-all.jar`)
- `commons-io-*.jar`
- `commons-logging-*.jar`
- `avalon-framework-*.jar`

You can copy all JARs at once:
- **Windows**: `xcopy /E /I "path\to\fop\lib\*" lib\`
- **Linux/macOS**: `cp path/to/fop/lib/*.jar lib/`

### 3. Compile the Java Code

Open a terminal in the project root directory and compile:

**On Windows:**
```bash
javac -cp "lib/*" -d out src\XmlToPdf.java
```

**On Linux/macOS:**
```bash
javac -cp "lib/*" -d out src/XmlToPdf.java
```

This command:
- Includes all JARs in `lib/` on the classpath (using wildcard `*`)
- Places compiled `.class` files into the `out/` directory
- Compiles `src/XmlToPdf.java`

### 4. Run the Program

Execute the compiled program:

**On Windows:**
```bash
java -cp "out;lib/*" XmlToPdf
```

**On Linux/macOS:**
```bash
java -cp "out:lib/*" XmlToPdf
```

**Note**: Windows uses semicolon (`;`) as the classpath separator, while Unix-like systems use colon (`:`).

### 5. Check Output

After successful execution, you should see:
```
PDF generated successfully.
```

The generated PDF will be located at `out/output.pdf`, containing the formatted book list from `src/data.xml`.

## How It Works

1. **FopFactory**: Creates a FOP factory instance (reusable for multiple documents)
2. **Output Stream**: Opens a buffered file output stream for the PDF
3. **Fop Object**: Creates a FOP instance configured for PDF output
4. **Transformer**: Uses JAXP TransformerFactory to load and apply the XSLT stylesheet
5. **Transformation**: Applies the XSLT to the XML, generating XSL-FO which FOP immediately renders to PDF

The XSLT stylesheet (`template.xsl`) transforms the XML data into XSL-FO (Formatting Objects), which FOP then renders as a PDF document.

## Customization

- **Modify XML Data**: Edit `src/data.xml` to use your own data structure
- **Change PDF Layout**: Edit `src/template.xsl` to adjust fonts, margins, page size, and styling
- **Output Location**: Modify the output path in `XmlToPdf.java` (currently `out/output.pdf`)

## Troubleshooting

- **ClassNotFoundException**: Ensure all FOP JAR files are in the `lib/` directory
- **FileNotFoundException**: Make sure `src/data.xml` and `src/template.xsl` exist
- **Compilation Errors**: Verify Java JDK is installed and `javac` is on your PATH
- **Path Issues**: On Windows, use backslashes (`\`) in file paths; on Unix-like systems, use forward slashes (`/`)

## References

- [Apache FOP Official Documentation](https://xmlgraphics.apache.org/fop/)
- [Apache FOP Downloads](https://xmlgraphics.apache.org/fop/download.html)

