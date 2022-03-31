import time
import helper
import config
import pymysql
import json


def menu():
    print("========================TOKO ENGINE MENU========================")
    print("===> ENGINE MODUL II IMS KELOMPOK 04")
    print("=====> 1. INTEGRATE DATA WITH JSON FILE")
    print("=====> 2. CREATE BACK UP DATA")
    print("=====> 3. EXIT")
    opsi = str(input("=====>ENTER : "))
    if (opsi == '1'):
        print("\n\n")
        integration_database()
        menu()
    elif (opsi == '2'):
        print("\n\n")
        backup_data()
        print("\n\n\n\n")
        menu()
    elif (opsi == '3'):
        print("\n\n")
        exit()
    else:
        print("TRY AGAIN\n\n")
        time.sleep(1)
        menu()


def backup_data():
    DB_1 = pymysql.connect(host='localhost', port=3308, user='root', password='', database='modul1_toko')
    DB_2 = pymysql.connect(host='localhost', port=3308, user='root', password='', database='modul1_bank')
    CUR_1 = DB_1.cursor()
    CUR_2 = DB_2.cursor()

    print("========================START BACKUP========================")
    data = {}

    data_tb_integrasi = 'SELECT * FROM tb_transaksi'
    CUR_2.execute(data_tb_integrasi)
    result_data_tb_integrasi = CUR_2.fetchall()
    DB_2.commit()

    data['tb_transaksi'] = []
    for dataIntegrasi in result_data_tb_integrasi:
        data['tb_transaksi'].append({
            'id_transaksi': str(dataIntegrasi[0]),
            'no_rekening': str(dataIntegrasi[1]),
            'tgl_rekening': str(dataIntegrasi[2]),
            'total_rekening': str(dataIntegrasi[3]),
            'status': str(dataIntegrasi[4])
        })
    writer = open('bank.json', 'w')
    writer.write(json.dumps(data, indent=4))
    writer.close()
    print('==> SUCCESS CREATE FILE BANK.json')

def integration_database():
    HISTORY_1 = config.FILE_2
    HISTORY_2 = config.FILE_1


    TB_NAME = "tb_transaksi"

    DB_1 = pymysql.connect(host='localhost', port=3308, user='root', password='', database='modul1_toko')
    DB_2 = pymysql.connect(host='localhost', port=3308, user='root', password='', database='modul1_bank')

    QUERY_SELECT = "SELECT * FROM tb_transaksi"

    while(True):
        CUR_1 = DB_1.cursor()
        CUR_2 = DB_2.cursor()

        CUR_1.execute(QUERY_SELECT)

        results = CUR_1.fetchall()

        history = helper.read_data(HISTORY_1)
        results = list(map(lambda x: tuple(map(str,x)),results))

        is_modified = False
        i = 0
        helper.sync_indexes.clear()
        for row in results:
            #found
            index = helper.find_by_id(history, row[0])
            if(index != -1):
                #modified
                if(row != history[index]):
                    helper.print_timestamp("row " + str(i) + " : modified")
                    print("row main\t: " + str(row))
                    print("row history\t: " + str(history[index]))
                    history[index] = row

                    query = helper.query_update_builder(TB_NAME, row)
                    helper.print_timestamp("EXECUTE QUERY : " + query)
                    # lakukan query update ke DB_2
                    CUR_2.execute(query);
                    is_modified = True

            #not found == insert
            else:
                query = helper.query_insert_builder(TB_NAME, row)
                helper.print_timestamp("EXECUTE QUERY : " + query)
                CUR_2.execute(query)

                history.append(row)
                index = helper.find_by_id(history, row[0])
                is_modified = True

            helper.sync_indexes.append(index)
            i += 1

        #delete
        if(len(helper.sync_indexes) < len(history)):
            i = 0
            while(i<len(history)):
                if(not helper.sync_indexes.__contains__(i)):
                    query = helper.query_delete_builder(TB_NAME, history[i])
                    helper.print_timestamp("EXECUTE QUERY : " + query)
                    CUR_2.execute(query)
                i+=1

            is_modified = True


        if (is_modified):
            helper.save_data(HISTORY_1, results)
            helper.save_data(HISTORY_2, results)
            helper.print_timestamp(HISTORY_1 +" & "+ HISTORY_2 +" has beed updated!")
        else:
            helper.print_timestamp("nothing changed")

        #commit and close cursor
        is_modified = False

        DB_1.commit()
        DB_2.commit()

        CUR_1.close()
        CUR_2.close()

        time.sleep(config.DELAY)

menu()