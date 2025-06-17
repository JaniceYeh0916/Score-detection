import pandas as pd
import re
import Levenshtein


def id_contrast(file_path, enter_list):

    def find_most_similar(A, B_list):
        similarities = [(B, Levenshtein.distance(A, B), idx) for idx, B in enumerate(B_list)]
        most_similar, min_distance, index = min(similarities, key=lambda x: x[1])
        return most_similar, min_distance, index

    file = pd.read_excel(file_path)
    id_data = file.iloc[:, 0].tolist()
    id_data_new = [re.sub(r'^[DM]', '', s) for s in id_data]
    name_data = file.iloc[:, 1].tolist()

    results = []
    for id, score in enter_list:
        id_new = id.replace('D', '').replace('M', '')

        if id == "-1":
            results.append((id, id, "-1", score))
            continue

        most_similar, distance, index = find_most_similar(id_new, id_data_new)
        results.append((id, id_data[index], name_data[index], score))

    return results


def write_file(file_path, enter_list, score_loc):
    file = pd.read_excel(file_path)
    allData = []
    for j in range(len(enter_list)):
        id = enter_list[j][0]
        score = enter_list[j][1]
        data = [id]
        for i in file.index:
            if file.iloc[i, 0] == id:
                file.loc[i, score_loc] = int(score)
                data.append(file.iloc[i, 1])
                data.append(score)
        allData.append(data)

    print(f"Finish!")
    file.to_excel(file_path, index=False)
    return allData


if __name__ == "__main__":
    file_path = "./student.xlsx"
    # id = 'D1159300'
    # score = 400
    # score_loc = '1/5'
    # data = write_file(file_path, [[id, score]], score_loc)
    # print(data)

    id = ["D1050957", "D158889", "D1159374", "D1126813", "D12786",
          "D183484", "D1103896", "D1012374", "D1683260", "10059"]
    score = [100, 95, 90, 85, 80, 75, 70, 65, 60, 55]

    enter_list = []
    for i in range(len(id)):
        enter_list.append([id[i], score[i]])

    result = id_contrast(file_path, enter_list)
    id_ori, id, name, score = map(list, zip(*result))
    print(id_ori, id, name, score)
