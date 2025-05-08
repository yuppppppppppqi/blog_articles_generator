import csv

input_file = 'massage_ratings_in_one_area.csv'
output_file = 'massage_ratings_in_one_area_replaced.csv'

with open(input_file, 'r', encoding='utf-8') as fin, open(output_file, 'w', encoding='utf-8', newline='') as fout:
    reader = csv.reader(fin)
    writer = csv.writer(fout)
    header = next(reader)
    writer.writerow(header)
    for row in reader:
        if row and ',' in row[0]:
            # ダブルクォートで囲まれている場合も考慮
            row[0] = row[0].replace(',', '+')
        writer.writerow(row)

print('変換が完了しました。新しいファイル:', output_file) 