import brightway2 as bw
import numpy as np
import pandas as pd

bw.projects.set_current("tryout")  # change me!

act = bw.Database('database_1').get('be0f50a058c54a23b1ec8e0518728673')
method = ('EF v3.1','climate change','global warming potential (GWP100)')

lca = bw.LCA({act:1}, method=method)

lca.lci()
lca.lcia()
lca.score

# transform the technosphere matrix to a more human-readable format
tech = lca.technosphere_matrix.toarray()
bio = lca.biosphere_matrix.toarray()
char = lca.characterization_matrix.toarray()


# Get all activities in the technosphere matrix
all_activities = [bw.Database(key[0]).get(key[1]) for key in lca.activity_dict.keys()]

# Collect all technosphere exchanges for all activities
exchange_list = []
for activity in all_activities:
    exchange_list.extend(list(activity.technosphere()))

def exchange_to_dict(exc):
    input_key = getattr(exc.input, 'key', (None, None))
    output_key = getattr(exc.output, 'key', (None, None))
    def get_name(key):
        try:
            db, code = key
            return bw.Database(db).get(code)['name']
        except Exception:
            return ''
    unc = exc._data.get('uncertainty', None)
    d = {
        'Input': get_name(input_key),
        'Input Database': input_key[0],
        'Input Code': input_key[1],
        'Output': get_name(output_key),
        'Output Database': output_key[0],
        'Output Code': output_key[1],
        'Amount': getattr(exc, 'amount', None),
        'Unit': exc._data.get('unit', None),
        'Uncertainty': unc,
        'Pedigree': unc.get('pedigree') if isinstance(unc, dict) else None,
        'loc': unc.get('loc') if isinstance(unc, dict) else None,
        'scale': unc.get('scale') if isinstance(unc, dict) else None,
        'shape': unc.get('shape') if isinstance(unc, dict) else None,
        'minimum': unc.get('minimum') if isinstance(unc, dict) else None,
        'maximum': unc.get('maximum') if isinstance(unc, dict) else None,
        'Formula': exc._data.get('formula', None),
    }
    return d

df = pd.DataFrame([exchange_to_dict(exc) for exc in exchange_list])
df.to_excel('all_technosphere_exchanges.xlsx', index=False)
print(f"Exported {len(df)} exchanges to all_technosphere_exchanges.xlsx")


print('Done')