# E-Invoice XML Converter

This project converts e-invoice files into XML format, extracting and mapping data correctly.

## Features

- Extracts invoice fields from various file formats (PDF, Excel, Word, JSON, CSV)
- Maps different variations of field names to the correct XML fields
- Formats dates in ISO format (YYYY-MM-DD)
- Uses dot (.) as the decimal separator for numbers
- Validates line items to ensure all required fields are present
- Provides clear warnings for missing required fields
- Outputs XML following the required schema

## XML Schema

The XML output follows this schema:

```xml
<Invoice>
    <InvoiceNumber></InvoiceNumber>
    <IssueDate></IssueDate>
    <Seller>
        <Name></Name>
        <VKN></VKN>
    </Seller>
    <Buyer>
        <Name></Name>
        <VKN></VKN>
    </Buyer>
    <Items>
        <Item>
            <Description></Description>
            <Quantity></Quantity>
            <UnitPrice></UnitPrice>
            <VAT></VAT>
            <Total></Total>
        </Item>
    </Items>
    <TotalAmount></TotalAmount>
    <Currency></Currency>
</Invoice>
```

## Usage

1. Run the application:
   ```
   python start_app.py
   ```

2. Upload an e-invoice file (PDF, Excel, Word, JSON, CSV)
3. The application will extract the data and convert it to XML
4. You can download the XML file or copy it to the clipboard

## Implementation Details

- **PDF Extractor**: Extracts data from PDF files using various patterns to handle different field names
- **XML Converter**: Converts the extracted data to XML following the required schema
- **Data Validation**: Validates the extracted data to ensure all required fields are present
- **Date Formatting**: Converts dates to ISO format (YYYY-MM-DD)
- **Number Formatting**: Uses dot (.) as the decimal separator for numbers

## Known Issues

- Some XML viewers may display `<Name>` tags as `<n>` tags due to display or encoding issues