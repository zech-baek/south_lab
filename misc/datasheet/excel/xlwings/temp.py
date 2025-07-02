import xlwings, os

def main():
    wb = xlwings.Book.caller()
    sht = wb.sheets[0]
    for i in range(1, 10):
        sht[f"A{i}"].value = f"automation {i:#04x}"

if __name__ == "__main__":
    print(os.getcwd())
    xlwings.Book("temp.xlsm").set_mock_caller()
    main()