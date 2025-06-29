import re
from collections import defaultdict
import pandas as pd
from .db_utils import get_db_connection


def process_ppt_pages(entry: str) -> str:
    try:
        entry = entry.strip()
        if ',' not in entry:
            return entry
        ranges = re.findall(r"'([^']+)'", entry)
        if not ranges:
            return entry + "无法处理"
        clean_ranges = []
        for r in ranges:
            parts = r.split('-', 1)
            if len(parts) == 2:
                base, end = parts
                clean_ranges.append((base.strip(), end.strip()))
            else:
                base = parts[0].strip()
                clean_ranges.append((base, base))
        grouped = defaultdict(list)
        for base, end in clean_ranges:
            grouped[base].append(end)
        processed_groups = []
        for base in sorted(grouped.keys(), key=lambda x: int(x)):
            ends = grouped[base]
            if not ends:
                return entry + "无法处理"
            first_end = ends[0]
            group_str = f"{base}-{first_end}"
            if len(ends) > 1:
                additional = '/'.join(ends[1:])
                group_str += f"/{additional}"
            processed_groups.append(f"'{group_str}'")
        final_str = ''.join(processed_groups)
        return final_str
    except Exception:
        return entry + "无法处理"


def aggregate_data(conn):
    df = pd.read_sql_query("SELECT * FROM extracted_data", conn)
    if df.empty:
        return
    def select_longest(group):
        ppt_pages = group['ppt_pages'].dropna().astype(str).tolist()
        ppt_pages_combined = ','.join(ppt_pages)
        descriptions = group['description'].fillna('')
        longest_description = descriptions.loc[descriptions.str.len().idxmax()]
        english_term = group['english'].iloc[0]
        return pd.Series({
            'english': english_term,
            'chinese': group.name,
            'ppt_pages': ppt_pages_combined,
            'description': longest_description
        })
    result_df = df.groupby('chinese').apply(select_longest).reset_index(drop=True)
    result_df['ppt_pages'] = result_df['ppt_pages'].astype(str).apply(process_ppt_pages)
    result_df.to_sql('aggregated_data', conn, if_exists='replace', index=False)

