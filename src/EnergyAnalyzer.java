import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import java.io.*;
import java.util.*;

public class EnergyAnalyzer {
    private String filePath;
    private List<Map<String, String>> records = new ArrayList<>();

    public EnergyAnalyzer(String filePath) {
        this.filePath = filePath;
    }

    public void readExcel() throws IOException {
        try (FileInputStream fis = new FileInputStream(filePath);
             Workbook workbook = new XSSFWorkbook(fis)) {

            Sheet sheet = workbook.getSheetAt(0);
            Iterator<Row> rows = sheet.iterator();

            Row header = rows.next();
            List<String> headers = new ArrayList<>();
            header.forEach(cell -> headers.add(cell.getStringCellValue().trim()));

            while (rows.hasNext()) {
                Row row = rows.next();
                Map<String, String> record = new HashMap<>();
                for (int i = 0; i < headers.size(); i++) {
                    Cell cell = row.getCell(i, Row.MissingCellPolicy.CREATE_NULL_AS_BLANK);
                    record.put(headers.get(i), cell.toString().trim());
                }
                records.add(record);
            }
        }
    }

    public void analyze() throws IOException {
        Map<String, Double> prevYear = new HashMap<>();
        List<String[]> output = new ArrayList<>();
        output.add(new String[]{"Year", "Source", "Value", "Growth (%)"});

        for (Map<String, String> row : records) {
            String year = row.get("Year");
            for (Map.Entry<String, String> entry : row.entrySet()) {
                String key = entry.getKey();
                if (key.equals("Year")) continue;
                try {
                    double value = Double.parseDouble(entry.getValue());
                    double growth = prevYear.containsKey(key)
                            ? ((value - prevYear.get(key)) / prevYear.get(key)) * 100
                            : 0.0;
                    output.add(new String[]{year, key, String.format("%.2f", value), String.format("%.2f", growth)});
                    prevYear.put(key, value);
                } catch (NumberFormatException ignored) {}
            }
        }

        try (PrintWriter pw = new PrintWriter(new FileWriter("output/renewable_summary.csv"))) {
            for (String[] line : output)
                pw.println(String.join(",", line));
        }

        System.out.println("✅ Analysis complete! Results saved to output/renewable_summary.csv");
    }
}
