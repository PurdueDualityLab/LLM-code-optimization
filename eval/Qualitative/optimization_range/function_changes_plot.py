import pandas as pd
import matplotlib.pyplot as plt

# Biojava data from user
biojava_data = pd.DataFrame({
    "file_name": [
        "AbstractSequence.java", "AminoAcidCompound.java", "AminoAcidCompoundSet.java",
        "CommandPrompt.java", "FastaReader.java", "GenericFastaHeaderParser.java",
        "PeptidePropertiesImpl.java", "ProteinSequence.java", "SequenceMixin.java",
        "Utils.java"
    ],
    "functions_compared": [68, 7, 17, 10, 5, 4, 36, 8, 25, 7],
    "functions_changed": [8, 6, 11, 6, 2, 4, 17, 4, 15, 6]
})

# Pmd
pmd_data = pd.DataFrame({
    "file_name": ["AbstractNode.java", "AbstractRule.java", "AttributeAxisIterator.java",
                  "ElementNode.java", "IOUtil.java", "RuleSetFactory.java",
                  "RuleSetFactoryCompatibility.java", "SaxonXPathRuleQuery.java", "XPathRule.java"],
    "functions_compared": [64, 63, 11, 21, 40, 30, 21, 16, 14],
    "functions_changed": [11, 8, 3, 3, 5, 8, 16, 4, 2]
})

# Graphchi
graphchi_data = pd.DataFrame({
    "file_name": ["ChiPointer.java", "ChiVertex.java", "DataBlockManager.java", "FloatConverter.java"],
    "functions_compared": [4, 24, 10, 3],
    "functions_changed": [3, 11, 6, 2]
})

# Fop
fop_data = pd.DataFrame({
    "file_name": ["AbstractPDFStream.java", "CharUtilities.java", "CommonFont.java", "DelegatingContentHandler.java",
                  "ElementMappingRegistry.java", "FObj.java", "FileIDGenerator.java", "FontSelector.java",
                  "FopFactoryBuilder.java", "InputHandler.java", "Main.java", "PDFDictionary.java",
                  "PDFICCStream.java", "PDFNumber.java", "PDFRoot.java", "PositionIterator.java",
                  "PropertyList.java", "TableLayoutManager.java"],
    "functions_compared": [21, 21, 15, 33, 9, 67, 9, 6, 102, 13, 9, 13, 6, 9, 44, 12, 40, 36],
    "functions_changed": [5, 9, 4, 13, 6, 16, 5, 3, 8, 8, 7, 5, 5, 3, 39, 6, 10, 9]
})

# Combine all app data into one DataFrame with app name
biojava_data['app'] = 'Biojava'
pmd_data['app'] = 'Pmd'
graphchi_data['app'] = 'Graphchi'
fop_data['app'] = 'Fop'

all_apps_df = pd.concat([biojava_data, pmd_data, graphchi_data, fop_data], ignore_index=True)

# Combined box plot for all four apps
fig, ax = plt.subplots(figsize=(6, 5))
bp = ax.boxplot(
    [all_apps_df[all_apps_df['app'] == app]['functions_changed'] for app in ['Biojava', 'Pmd', 'Graphchi', 'Fop']],
    vert=True, patch_artist=True, tick_labels=['Biojava', 'Pmd', 'Graphchi', 'Fop']
)

# Color all boxes light gray
for box in bp['boxes']:
    box.set(facecolor='lightgray')

ax.set_ylabel("Number of Functions Changed Each Class File")
ax.set_title("Distribution of Functions Changed for Each App")

plt.tight_layout()
fig_path = 'function_changes_boxplot_all_apps.png'
plt.savefig(fig_path, dpi=200)
plt.show()
fig_path