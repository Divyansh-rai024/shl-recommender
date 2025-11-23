import pandas as pd
import requests
import os

API_URL = os.environ.get('RECOMMEND_API', 'http://localhost:8000')
EXCEL_PATH = '/mnt/data/Gen_AI Dataset.xlsx'
OUT_CSV = '../submission/submission.csv'

def main():
    df = pd.read_excel(EXCEL_PATH, sheet_name=0)
    possible_cols = [c for c in df.columns if 'query' in c.lower() or 'text' in c.lower() or 'job' in c.lower()]
    if not possible_cols:
        raise ValueError('Could not find query column in the Excel. Columns: ' + ', '.join(df.columns))
    col = possible_cols[0]
    rows = []
    for q in df[col].astype(str).tolist():
        r = requests.post(f"{API_URL}/recommend", json={"query": q, "max_results": 10}, timeout=30)
        if r.status_code != 200:
            print('API error for query:', q, r.status_code, r.text)
            continue
        recs = r.json()['recommendations']
        for rec in recs:
            rows.append({'Query': q, 'Assessment_url': rec['assessment_url']})
    out_df = pd.DataFrame(rows)
    os.makedirs('../submission', exist_ok=True)
    out_df.to_csv(OUT_CSV, index=False)
    print('Saved submission CSV to', OUT_CSV)

if __name__ == '__main__':
    main()
