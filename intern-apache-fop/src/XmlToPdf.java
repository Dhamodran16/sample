import java.io.*;
import javax.xml.transform.*;
import javax.xml.transform.stream.*;
import javax.xml.transform.sax.SAXResult;
import org.apache.fop.apps.*;

public class XmlToPdf {
    public static void main(String[] args) {
        try {
            // Step 1: Construct FopFactory (can use default config)
            FopFactory fopFactory = FopFactory.newInstance(new File(".").toURI());
            
            // Step 2: Set up output stream for PDF
            OutputStream out = new BufferedOutputStream(new FileOutputStream("out/output.pdf"));
            
            try {
                // Step 3: Create Fop with desired output format (PDF)
                Fop fop = fopFactory.newFop(MimeConstants.MIME_PDF, out);
                
                // Step 4: Setup JAXP transformer with our XSLT stylesheet
                TransformerFactory factory = TransformerFactory.newInstance();
                Transformer transformer = factory.newTransformer(new StreamSource(new File("src/template.xsl")));
                
                // Step 5: Setup input XML and result (the SAX events sent to FOP)
                Source src = new StreamSource(new File("src/data.xml"));
                Result res = new SAXResult(fop.getDefaultHandler());
                
                // Step 6: Transform XML to XSL-FO and let FOP write the PDF
                transformer.transform(src, res);
            } finally {
                out.close();
            }
            System.out.println("PDF generated successfully.");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}