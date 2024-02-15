import pandas as pd
import requests as rq
import bs4
def seasonToAbbrev(string):
    if string == "Fall":
        return "FA"
    if string == "Spring":
        return "SP"
    if string == "Summer":
        return "SU"
    if string == "Winter":
        return "WI"
        
ROSTER_START_URL = "https://classes.cornell.edu/browse/roster/"
"""_summary_
Class roster url structure:
    https://classes.cornell.edu/browse/roster/[SEASON ABREV.][LAST TWO OF YEAR]/class/[3 LETTER DEPT. DISTINCTION]/[COURSE NUMBER]
    I.E.,
    https://classes.cornell.edu/browse/roster/SP24/class/CHEM/1008
"""
data = pd.read_excel("input.xlsx")
cleaned_data = pd.DataFrame(columns=['Dept', 'Class No.','Season','Year'])
cleaned_data[['Dept', 'Class No.']] = data["Course"].str.split(' ', expand=True)
cleaned_data[['Season', 'Year']] = data['Year'].str.replace("20", "").str.split(' ', expand=True)
cleaned_data['Season'] = cleaned_data['Season'].apply(lambda x: seasonToAbbrev(x))
cleaned_data = cleaned_data.apply(lambda x: x.str.strip())

output = pd.DataFrame(columns=["Course", "Desc", "Outcomes"])
data_len = cleaned_data.shape[0]

for x in range(int(data_len)):
    built_url = ROSTER_START_URL + f"{cleaned_data['Season'][x]}{cleaned_data['Year'][x]}/class/{cleaned_data['Dept'][x]}/{cleaned_data['Class No.'][x]}"
    print(built_url)
    html_content = rq.get(built_url)
    soup = bs4.BeautifulSoup(html_content.content, "html5lib")
    course_listing = soup.find('div', class_='class-listing')
    course_desc = course_listing.find('p', class_="catalog-descr") if course_listing else None
    #Two no good one liners...
    #"\r\n".join(str(x) for x in course_listing.find('ul', class_="circle").find_all('li')) #[x for x in course_listing.find('ul', class_="circle").find_all('li')]

    course_outcomes= course_listing.find('ul', class_="circle") if course_listing else None
    course_outcome = ""
    if course_outcomes:
        for outcome in course_outcomes.find_all('li'):
            if outcome:
                course_outcome = course_outcome + outcome.text + "\n\r" 
    if course_desc:
        new_row = {"Course":f"{cleaned_data['Dept'][x]}{cleaned_data['Class No.'][x]}" , "Desc": course_desc.text, "Outcomes": course_outcome}
    else:
        new_row = {"Course":f"{cleaned_data['Dept'][x]}{cleaned_data['Class No.'][x]}" , "Desc": "No valid course listing found", "Outcomes": "No valid course listing found "}

    temp_df = pd.DataFrame([new_row])
    output = pd.concat([output, temp_df], ignore_index=True)
output_file = "output.xlsx"
output.to_excel(output_file)
    
    
    
    





