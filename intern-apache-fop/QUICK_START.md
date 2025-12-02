# Quick Start Guide - Commands to Run

## Setup (One-time only)

### 1. Copy Apache FOP JAR files to project

**Copy dependency JARs:**
```powershell
Copy-Item "C:\Users\dhamo\Downloads\fop-2.11-bin\fop-2.11\fop\lib\*.jar" -Destination "lib\" -Force
```

**Copy FOP core JARs:**
```powershell
Copy-Item "C:\Users\dhamo\Downloads\fop-2.11-bin\fop-2.11\fop\build\*.jar" -Destination "lib\" -Force
```

## Compile and Run (Every time you make changes)

### 2. Compile the Java code

```powershell
javac -cp "lib/*" -d out src\XmlToPdf.java
```

**Alternative (if wildcard doesn't work):**
```powershell
javac -cp "lib\fop-2.11.jar;lib\xmlgraphics-commons-2.11.jar;lib\batik-*.jar;lib\commons-*.jar;lib\*.jar" -d out src\XmlToPdf.java
```

### 3. Run the application

```powershell
java -cp "out;lib/*" XmlToPdf
```

**Alternative (if wildcard doesn't work):**
```powershell
java -cp "out;lib\fop-2.11.jar;lib\fop-core-2.11.jar;lib\fop-events-2.11.jar;lib\fop-util-2.11.jar;lib\xmlgraphics-commons-2.11.jar;lib\batik-*.jar;lib\commons-*.jar;lib\*.jar" XmlToPdf
```

## Output

After successful execution, you should see:
```
PDF generated successfully.
```

The generated PDF will be at: `out\output.pdf`

## All-in-One Commands

**To compile and run in one go:**
```powershell
javac -cp "lib/*" -d out src\XmlToPdf.java; if ($?) { java -cp "out;lib/*" XmlToPdf }
```

## Troubleshooting

- If you get "cannot find symbol" errors, make sure all JAR files are in the `lib/` directory
- If compilation fails, check that Java JDK is installed: `java -version` and `javac -version`
- Font warnings (Symbol, ZapfDingbats) are normal and don't affect functionality

