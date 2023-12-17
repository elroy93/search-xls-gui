import xlwings as xw
from faker import Faker
import random
import locale
import os

app = xw.App(visible=False, add_book=False)
fake = Faker("zh_CN")
locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')

def generate_data(num_rows=10, filename='data.xlsx'):
    print(f"generate_data:filename={filename}")
    # 如果文件存在则删除
    if os.path.exists(filename):
        os.remove(filename)

    # 创建Excel工作簿
    wb = app.books.add()
    sheet = wb.sheets['Sheet1']

    # 设置列标题
    sheet.range('A1').value = '姓名'
    sheet.range('B1').value = '年龄'
    sheet.range('C1').value = '邮箱'

    # 生成并写入数据
    for row in range(2, num_rows + 2):
        name = fake.name()
        age = random.randint(18, 60)  # 假设年龄在18到60岁之间
        email = fake.email()
        print("name=", name, "age=", age, "email=", email)
        # 写入每行数据
        sheet.range(f'A{row}').value = name
        sheet.range(f'B{row}').value = age
        sheet.range(f'C{row}').value = email

    # 保存工作簿
    wb.save(filename)
    print("save :filename=", filename)
    wb.close()

if __name__ == '__main__':
    for i in range(10):
        generate_data(filename="data"+str(i)+".xlsx")