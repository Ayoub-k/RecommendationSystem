import mysql.connector as connection
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
tf = TfidfVectorizer(analyzer='word',ngram_range=(1, 2),min_df=0, stop_words='english')
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
# from fuzzywuzzy import process


def conction_db():
    return connection.connect(host="localhost", database = 'iferu',user="max", passwd="toor",use_pure=True)

def test_user(user_name):
    try:
        mydb = conction_db()
        mycursor = mydb.cursor()
        mycursor.execute(f"SELECT * FROM `user_table` where user_name= %s", (user_name, ))
        myresult = mycursor.fetchall()
        mydb.close()
        if myresult != [] and len(myresult) > 0:
            return True
        return False
    except Exception as e:
        mydb.close()
        return False

def get_ids_books(user_name):
    try:
        mydb = conction_db()
        mycursor = mydb.cursor()
        mycursor.execute("SELECT idDoc FROM `user_like` where user_name= %s", (user_name, ))
        myresult = mycursor.fetchall()
        if len(myresult) > 0:
            return [id[0] for id in myresult]
        return []
        mydb.close()
    except Exception as e:
        mydb.close()
        return []

def get_liked_books(user_name):
    try:
        mydb = conction_db()
        query1 = "SELECT id, titre, isbn, description, linked_channel  FROM `Document` where id in "+str(tuple(get_ids_books(user_name)))
        query2 = "select id as linked_channel, nom_en as chaine from Chaine "
        book   = pd.read_sql(query1,mydb)
        chaine = pd.read_sql(query2,mydb)
        mydb.close()
        chaine['linked_channel'] = chaine['linked_channel'].astype(str)
        book['linked_channel'] = book.linked_channel.apply(lambda x: x.split(';')[0])
        df_ = book[['id', 'titre', 'description', 'isbn', 'linked_channel']].merge(chaine[['linked_channel', 'chaine']], on='linked_channel')
        return df_
    except Exception as e:
        mydb.close()
        print(str(e))
        return []

def data_set():
    try:
        mydb = conction_db()
        query1 = "SELECT id, titre, isbn, description, linked_channel  FROM `Document` where type='book' ; "
        query2 = "select id as linked_channel, nom_en as chaine from Chaine "
        book   = pd.read_sql(query1,mydb)
        chaine = pd.read_sql(query2,mydb)
        chaine['linked_channel'] = chaine['linked_channel'].astype(str)
        book['linked_channel'] = book.linked_channel.apply(lambda x: x.split(';')[0])
        df_final = book[['id', 'titre', 'description', 'isbn', 'linked_channel']].merge(chaine[['linked_channel', 'chaine']], on='linked_channel')
        df_final['description'] = df_final['description'].astype(str)
        mydb.close()
        return df_final
    except Exception as e:
        mydb.close()
        return []

def recommandation(title, chaine):
    df_final_ = data_set()
    df_final_ = df_final_[df_final_['chaine'] == chaine]
    # df_final_['description'] =  df_final_['description'].apply(lambda x: " " if type(x) == 'float' else x )
    tfidf_matrix = tf.fit_transform(df_final_['description'].astype(str))
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    df_final_ = df_final_.reset_index()
    titles = df_final_['titre']
    indices = pd.Series(df_final_.index, index=df_final_['titre'])
    index = indices[title]
    sim_scores = list(enumerate(cosine_sim[index]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:10]
    livre_indices = [i[0] for i in sim_scores]
    reco = [] 
    for k, v in titles.iloc[livre_indices].items():
        reco.append(v)
    return reco



def books_recommend(user_name):
    book_liked = get_liked_books(user_name)[['titre', 'chaine']]
    book_recommanded = []
    for book in book_liked.values:
        try:
            book_recommanded.append(recommandation(book[0], book[1]))
        except Exception as e:
            pass
    recommended_ = []
    for bo in book_recommanded:
        for b in bo:
            recommended_.append(b)
    return recommended_


def all_book_recommanded(user_name):
    name_book = books_recommend(user_name)
    liste_books = []
    try:
        mydb = conction_db()
        mycursor = mydb.cursor()
        for name in name_book:
            mycursor.execute(f"SELECT D.id, titre, type, image, date, number FROM Document D, Rating R  where D.idRating=R.id and titre= %s", (name, ))
            myresult = mycursor.fetchall()
            dic = dict()
            dic['id'] = myresult[0][0]
            dic['titre'] = myresult[0][1]
            dic['type'] = myresult[0][2]
            dic['image'] = myresult[0][3]
            dic['averge_rating'] = myresult[0][5]
            liste_books.append(dic)
        mydb.close()
        dic = dict()
        dic['data'] = liste_books
        return dic
    except Exception as e:
        print(str(e))
        return []

# print(all_book_recommanded('admin'))
