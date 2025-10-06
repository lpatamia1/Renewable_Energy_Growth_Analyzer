public class Main {
    public static void main(String[] args) {
        try {
            EnergyAnalyzer analyzer = new EnergyAnalyzer("data/Table_10.1_Renewable_Energy_Production_and_Consumption_by_Source.xlsx");
            analyzer.readExcel();
            analyzer.analyze();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
