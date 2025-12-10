import brightway2 as bw

bw.projects.set_current("tryout")  # change me!

act = bw.Database('database_1').get('be0f50a058c54a23b1ec8e0518728673')
method = ('EF v3.1','climate change','global warming potential (GWP100)')

lca = bw.LCA({act:1}, method=method)

lca.lci()
lca.lcia()
lca.score

# transform the technosphere matrix to a more human-readable format
lca.technosphere_matrix.toarray()
lca.biosphere_matrix.toarray()
lca.characterization_matrix.toarray()

print('Done')