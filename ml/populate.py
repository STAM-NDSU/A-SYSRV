import pandas as pd
import sqlite3
from Bio import SeqIO
from Bio.SeqUtils.ProtParam import ProteinAnalysis
import json
import os
import sqlite3
import json
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)



def populate_db(fasta_file, json_file, db_dir, tsv_directory):
    # Connect to the SQLite database (it will be created if it doesn't exist)
    conn = sqlite3.connect(db_dir)
    cur = conn.cursor()

    # drop proteins table
    cur.execute('''DROP TABLE IF EXISTS proteins''')
    conn.commit()


    # Create the table with the necessary columns
    cur.execute('''CREATE TABLE IF NOT EXISTS proteins (
        seq_id TEXT PRIMARY KEY,
        description TEXT,
        sequence TEXT,
        length INTEGER,
        molecular_weight REAL,
        instability_index REAL,
        isoelectric_point REAL,
        gravy REAL,
        amino_count TEXT,
        aromaticity REAL,
        flexibility TEXT,
        secondary_structure_fraction TEXT,
        molar_extinction_coefficient TEXT
    )''')
    conn.commit()

    ############

    # Drop the 'metadata' table if it exists
    cur.execute('''DROP TABLE IF EXISTS metadata''')
    conn.commit()  # Commit the changes

    # Create the 'metadata' table
    cur.execute('''
        CREATE TABLE metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            primaryAccession TEXT,
            annotationScore INTEGER,
            comments TEXT,
            keywords TEXT,
            uniProtKBCrossReferences TEXT
        )
    ''')
    conn.commit()  # Commit the changes


    #############

    def insert_proteins(records):
        # Prepare bulk insert statements
        cur.executemany('''INSERT INTO proteins (seq_id, description, sequence, length, molecular_weight, 
        instability_index, isoelectric_point, gravy, amino_count, aromaticity, flexibility, 
        secondary_structure_fraction, molar_extinction_coefficient) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', records)

    # It's often a good idea to disable journaling and synchronous writes for large bulk inserts.
    # Don't forget to enable them again if needed for your application's integrity requirements.
    conn.execute('PRAGMA journal_mode = OFF')
    conn.execute('PRAGMA synchronous = OFF')

    # You can also increase cache size
    conn.execute('PRAGMA cache_size = 3000') # Adjust the cache size to your needs.

    # Collect records in batches
    batch_size = 500  # You can tune this number
    batch_records = []

    with open(fasta_file, 'r') as fasta_file:
        for record in SeqIO.parse(fasta_file, 'fasta'):
            sequence = str(record.seq)
            seq_id = record.id.split("|")[1].strip()
            length = len(sequence)
            description = record.description

            placeholders = (None,) * 9

            if "X" in sequence or "U" in sequence:
                batch_records.append((seq_id, description, sequence, length) + placeholders)
            else:
                a_seq = ProteinAnalysis(sequence)
                m_weight = a_seq.molecular_weight()
                instab_index = a_seq.instability_index()
                isoele_point = a_seq.isoelectric_point()
                gravy = a_seq.gravy()
                amino_count = a_seq.count_amino_acids()
                amino_count_json = json.dumps(amino_count)
                aromaticity = a_seq.aromaticity()
                flexibility = a_seq.flexibility()
                flexibility_json = json.dumps(flexibility)
                sec_struct_frac = a_seq.secondary_structure_fraction()
                sec_struct_frac_json = json.dumps(sec_struct_frac)
                ext_coeff = a_seq.molar_extinction_coefficient()
                ext_coeff_json = json.dumps(ext_coeff)

                batch_records.append((seq_id, description, sequence, length, m_weight, instab_index, isoele_point, gravy, amino_count_json, aromaticity, flexibility_json, sec_struct_frac_json, ext_coeff_json))
            
            # Insert in batches
            if len(batch_records) >= batch_size:
                insert_proteins(batch_records)
                batch_records = []  # Reset batch

    # Insert any remaining records
    if batch_records:
        insert_proteins(batch_records)

    # Commit and clean up
    conn.commit()


    #############

    def insert_records(records):
        # Prepare the data for insertion, ensuring that all list or dict types are converted to JSON strings
        prepared_records = []
        for record in records:
            prepared_record = tuple(
                json.dumps(item) if isinstance(item, (list, dict)) else item
                for item in record
            )
            prepared_records.append(prepared_record)

        # Use executemany to insert all records in one go
        cur.executemany('''
            INSERT INTO metadata (
                primaryAccession, 
                annotationScore, 
                comments, 
                keywords, 
                uniProtKBCrossReferences
            ) VALUES (?, ?, ?, ?, ?)
        ''', prepared_records)
        conn.commit()


    # Assuming 'your_json_file.json' is in the same directory as your script
    with open(json_file, 'r') as f:
        data = json.load(f)

    # log length of data
    logger.info(f"length of data: {len(data)}")

    batch_records2 = []

    for primary_accession, item in data.items():
        
        # Extract data using the keys directly from the item
        record = (
            primary_accession,
            item.get('annotationScore'),
            json.dumps(item.get('comments')) if isinstance(item.get('comments'), list) else item.get('comments'),
            json.dumps(item.get('keywords')) if isinstance(item.get('keywords'), list) else item.get('keywords'),
            json.dumps(item.get('uniProtKBCrossReferences')) if isinstance(item.get('uniProtKBCrossReferences'), list) else item.get('uniProtKBCrossReferences'),
        )   
        batch_records2.append(record)

        if len(batch_records2) >= batch_size:
            insert_records(batch_records2)
            batch_records2 = []  # Reset the batch

    # Insert any remaining records
    if batch_records2:
        insert_records(batch_records2)

    # Commit the transaction
    conn.commit()

    # Re-enable journaling and synchronous writes
    cur.execute('PRAGMA journal_mode = DELETE')  # Set it back to the default or your preferred mode
    cur.execute('PRAGMA synchronous = NORMAL')   # Set it back to the default or your preferred mode

    #############

    # Iterate through each TSV file in the directory
    for tsv_filename in os.listdir(tsv_directory):
        if tsv_filename.endswith('.tsv'):
            # Construct the full file path
            file_path = os.path.join(tsv_directory, tsv_filename)
            
            # Read the TSV file into a DataFrame
            df = pd.read_csv(file_path, sep='\t', encoding='utf-8')

            # Extract protein_id and remove the '#' column
            df['protein_id'] = df['#'].apply(lambda x: x.split("|")[1].strip())
            
            # Get the file name without the .tsv extension
            file_name = tsv_filename[:-4]
            
            # Add the file name as a prefix to all columns except 'protein_id'
            df.columns = [f"{file_name}_{col}" if col != 'protein_id' else col for col in df.columns]
            
            #log df
            #logger.info(f"df: {df}")
            
            # TODO: why some dfs are not written to sql?

            # Use 'to_sql' method to write the DataFrame to the SQLite table
            try:
                df.to_sql(file_name, conn, if_exists='replace', index=False)
            except Exception as e:
                logger.error(f"Error writing to SQL: {e}")
            conn.commit()

    # Create the table with the necessary columns
    cur.execute('''
        CREATE TABLE merged_data AS
        SELECT
            m.*,
            p.*,
            CTDC.*,
            CTDD.*,
            CTDT.*,
            CTriad.*,
            DPC.*,
            GAAC.*
        FROM
            metadata m
            LEFT JOIN proteins p ON m.primaryAccession = p.seq_id
            LEFT JOIN CTDC ON m.primaryAccession = CTDC.protein_id
            LEFT JOIN CTDD ON m.primaryAccession = CTDD.protein_id
            LEFT JOIN CTDT ON m.primaryAccession = CTDT.protein_id
            LEFT JOIN CTriad ON m.primaryAccession = CTriad.protein_id
            LEFT JOIN DPC ON m.primaryAccession = DPC.protein_id
            LEFT JOIN GAAC ON m.primaryAccession = GAAC.protein_id;
    ''')

    #drop tables
    cur.execute('''DROP TABLE IF EXISTS CTDC''')
    cur.execute('''DROP TABLE IF EXISTS CTDD''')
    cur.execute('''DROP TABLE IF EXISTS CTDT''')
    cur.execute('''DROP TABLE IF EXISTS CTriad''')
    cur.execute('''DROP TABLE IF EXISTS DPC''')
    cur.execute('''DROP TABLE IF EXISTS GAAC''')
    cur.execute('''DROP TABLE IF EXISTS proteins''')
    cur.execute('''DROP TABLE IF EXISTS metadata''')

    #########
    cur.executescript('''
        ---sql
        CREATE TABLE new_merged_data AS
        SELECT
            *,
            (
            SELECT json_group_array(json_extract(loc.value, '$.location.value'))
            FROM json_each(json_extract(t.comments, '$')) AS entry
            LEFT JOIN json_each(json_extract(entry.value, '$.subcellularLocations')) AS loc
            WHERE json_extract(entry.value, '$.commentType') = 'SUBCELLULAR LOCATION'
            ) AS location_values
        FROM merged_data AS t;

        ---sql
        drop table merged_data;

        ALTER TABLE new_merged_data ADD COLUMN cytoplasm INTEGER;
        ALTER TABLE new_merged_data ADD COLUMN cell_membrane INTEGER;
        ALTER TABLE new_merged_data ADD COLUMN cell_wall INTEGER;
        ALTER TABLE new_merged_data ADD COLUMN secreted INTEGER;
        ALTER TABLE new_merged_data ADD COLUMN periplasm INTEGER;
        ALTER TABLE new_merged_data ADD COLUMN cell_surface INTEGER;
        ALTER TABLE new_merged_data ADD COLUMN cell_envelope INTEGER;
        ALTER TABLE new_merged_data ADD COLUMN chlorosome INTEGER;
        ALTER TABLE new_merged_data ADD COLUMN cellular_thylakoid_membrane INTEGER;
        ALTER TABLE new_merged_data ADD COLUMN cellular_chromatopore_membrane INTEGER;
        ALTER TABLE new_merged_data ADD COLUMN single_pass_membrane_protein INTEGER;
        ALTER TABLE new_merged_data ADD COLUMN multi_pass_membrane_protein INTEGER;
        ALTER TABLE new_merged_data ADD COLUMN peripheral_membrane_protein INTEGER;

        ---sql
        UPDATE new_merged_data
        SET
        cytoplasm = CASE 
            WHEN location_values LIKE '%"Cytoplasm"%' 
            OR location_values LIKE '%"Cytoplasmic side"%' 
            OR location_values LIKE '%"Cytoplasm, nucleoid"%' THEN 1 ELSE 0 END,
        cell_membrane = CASE 
            WHEN location_values LIKE '%"Cell membrane"%' 
            OR location_values LIKE '%"Membrane"%' 
            OR location_values LIKE '%"Cell inner membrane"%' 
            OR location_values LIKE '%"Cell outer membrane"%' THEN 1 ELSE 0 END,
        cell_wall = CASE WHEN location_values LIKE '%"Cell wall"%' THEN 1 ELSE 0 END,
        secreted = CASE WHEN location_values LIKE '%"Secreted"%' THEN 1 ELSE 0 END,
        periplasm = CASE 
            WHEN location_values LIKE '%"Periplasm"%' 
            OR location_values LIKE '%"Periplasmic side"%' THEN 1 ELSE 0 END,
        cell_surface = CASE WHEN location_values LIKE '%"Cell surface"%' THEN 1 ELSE 0 END,
        cell_envelope = CASE WHEN location_values LIKE '%"Cell envelope"%' THEN 1 ELSE 0 END,
        chlorosome = CASE WHEN location_values LIKE '%"Chlorosome"%' THEN 1 ELSE 0 END,
        cellular_thylakoid_membrane = CASE WHEN location_values LIKE '%"Cellular thylakoid membrane"%' THEN 1 ELSE 0 END,
        cellular_chromatopore_membrane = CASE WHEN location_values LIKE '%"Cellular chromatopore membrane"%' THEN 1 ELSE 0 END,
        single_pass_membrane_protein = CASE WHEN location_values LIKE '%"Single-pass membrane protein"%' THEN 1 ELSE 0 END,
        multi_pass_membrane_protein = CASE WHEN location_values LIKE '%"Multi-pass membrane protein"%' THEN 1 ELSE 0 END,
        peripheral_membrane_protein = CASE WHEN location_values LIKE '%"Peripheral membrane protein"%' THEN 1 ELSE 0 END;

        ''')
    
    conn.commit()

    ############

    cur.executescript('''
        --- data binding
        ALTER TABLE new_merged_data ADD COLUMN dna_binding INTEGER;
        ALTER TABLE new_merged_data ADD COLUMN rna_binding INTEGER;
        ALTER TABLE new_merged_data ADD COLUMN metal_binding INTEGER;

        UPDATE new_merged_data
        SET
        dna_binding = CASE WHEN keywords LIKE '%"DNA-binding"%' THEN 1 ELSE 0 END,
        rna_binding = CASE WHEN keywords LIKE '%"RNA-binding"%' THEN 1 ELSE 0 END,
        metal_binding = CASE WHEN keywords LIKE '%"Metal-binding"%' THEN 1 ELSE 0 END;

        ''')

    conn.commit()

    ############

    cur.executescript('''
        ALTER TABLE new_merged_data ADD COLUMN GO_0051287 INTEGER DEFAULT 0;
        ALTER TABLE new_merged_data ADD COLUMN GO_0009331 INTEGER DEFAULT 0;
        ALTER TABLE new_merged_data ADD COLUMN GO_0003677 INTEGER DEFAULT 0;
        ALTER TABLE new_merged_data ADD COLUMN GO_0003723 INTEGER DEFAULT 0;
        ALTER TABLE new_merged_data ADD COLUMN GO_0005506 INTEGER DEFAULT 0;
        ALTER TABLE new_merged_data ADD COLUMN GO_0005524 INTEGER DEFAULT 0;
        ALTER TABLE new_merged_data ADD COLUMN GO_0046167 INTEGER DEFAULT 0;
        ALTER TABLE new_merged_data ADD COLUMN GO_0008270 INTEGER DEFAULT 0;
        ALTER TABLE new_merged_data ADD COLUMN GO_0016887 INTEGER DEFAULT 0;
        ALTER TABLE new_merged_data ADD COLUMN GO_0019843 INTEGER DEFAULT 0;
        ALTER TABLE new_merged_data ADD COLUMN GO_0008654 INTEGER DEFAULT 0;
        ALTER TABLE new_merged_data ADD COLUMN GO_0046872 INTEGER DEFAULT 0;
        ALTER TABLE new_merged_data ADD COLUMN GO_0050661 INTEGER DEFAULT 0;
        ALTER TABLE new_merged_data ADD COLUMN GO_0051539 INTEGER DEFAULT 0;


        UPDATE new_merged_data
        SET
        GO_0051287 = CASE WHEN uniProtKBCrossReferences LIKE '%"GO:0051287"%' THEN 1 ELSE 0 END,
        GO_0009331 = CASE WHEN uniProtKBCrossReferences LIKE '%"GO:0009331"%' THEN 1 ELSE 0 END,
        GO_0003677 = CASE WHEN uniProtKBCrossReferences LIKE '%"GO:0003677"%' THEN 1 ELSE 0 END,
        GO_0003723 = CASE WHEN uniProtKBCrossReferences LIKE '%"GO:0003723"%' THEN 1 ELSE 0 END,
        GO_0005506 = CASE WHEN uniProtKBCrossReferences LIKE '%"GO:0005506"%' THEN 1 ELSE 0 END,
        GO_0005524 = CASE WHEN uniProtKBCrossReferences LIKE '%"GO:0005524"%' THEN 1 ELSE 0 END,
        GO_0046167 = CASE WHEN uniProtKBCrossReferences LIKE '%"GO:0046167"%' THEN 1 ELSE 0 END,
        GO_0008270 = CASE WHEN uniProtKBCrossReferences LIKE '%"GO:0008270"%' THEN 1 ELSE 0 END,
        GO_0016887 = CASE WHEN uniProtKBCrossReferences LIKE '%"GO:0016887"%' THEN 1 ELSE 0 END,
        GO_0019843 = CASE WHEN uniProtKBCrossReferences LIKE '%"GO:0019843"%' THEN 1 ELSE 0 END,
        GO_0008654 = CASE WHEN uniProtKBCrossReferences LIKE '%"GO:0008654"%' THEN 1 ELSE 0 END,
        GO_0046872 = CASE WHEN uniProtKBCrossReferences LIKE '%"GO:0046872"%' THEN 1 ELSE 0 END,
        GO_0050661 = CASE WHEN uniProtKBCrossReferences LIKE '%"GO:0050661"%' THEN 1 ELSE 0 END,
        GO_0051539 = CASE WHEN uniProtKBCrossReferences LIKE '%"GO:0051539"%' THEN 1 ELSE 0 END;
        ''')

    conn.commit()

    ############

    cur.executescript('''
        ALTER TABLE new_merged_data ADD COLUMN A INTEGER;
        ALTER TABLE new_merged_data ADD COLUMN C INTEGER;
        ALTER TABLE new_merged_data ADD COLUMN D INTEGER;
        ALTER TABLE new_merged_data ADD COLUMN E INTEGER;
        ALTER TABLE new_merged_data ADD COLUMN F INTEGER;
        ALTER TABLE new_merged_data ADD COLUMN G INTEGER;
        ALTER TABLE new_merged_data ADD COLUMN H INTEGER;
        ALTER TABLE new_merged_data ADD COLUMN I INTEGER;
        ALTER TABLE new_merged_data ADD COLUMN K INTEGER;
        ALTER TABLE new_merged_data ADD COLUMN L INTEGER;
        ALTER TABLE new_merged_data ADD COLUMN M INTEGER;
        ALTER TABLE new_merged_data ADD COLUMN N INTEGER;
        ALTER TABLE new_merged_data ADD COLUMN P INTEGER;
        ALTER TABLE new_merged_data ADD COLUMN Q INTEGER;
        ALTER TABLE new_merged_data ADD COLUMN R INTEGER;
        ALTER TABLE new_merged_data ADD COLUMN S INTEGER;
        ALTER TABLE new_merged_data ADD COLUMN T INTEGER;
        ALTER TABLE new_merged_data ADD COLUMN V INTEGER;
        ALTER TABLE new_merged_data ADD COLUMN W INTEGER;
        ALTER TABLE new_merged_data ADD COLUMN Y INTEGER;

        UPDATE new_merged_data
        SET 
            A = json_extract(amino_count, '$.A'),
            C = json_extract(amino_count, '$.C'),
            D = json_extract(amino_count, '$.D'),
            E = json_extract(amino_count, '$.E'),
            F = json_extract(amino_count, '$.F'),
            G = json_extract(amino_count, '$.G'),
            H = json_extract(amino_count, '$.H'),
            I = json_extract(amino_count, '$.I'),
            K = json_extract(amino_count, '$.K'),
            L = json_extract(amino_count, '$.L'),
            M = json_extract(amino_count, '$.M'),
            N = json_extract(amino_count, '$.N'),
            P = json_extract(amino_count, '$.P'),
            Q = json_extract(amino_count, '$.Q'),
            R = json_extract(amino_count, '$.R'),
            S = json_extract(amino_count, '$.S'),
            T = json_extract(amino_count, '$.T'),
            V = json_extract(amino_count, '$.V'),
            W = json_extract(amino_count, '$.W'),
            Y = json_extract(amino_count, '$.Y');

            ''')

    conn.commit()   

    ############

    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(new_merged_data);")
    columns = [row[1] for row in cursor.fetchall() if row[1].startswith('protein_id')]

    # Drop each of these columns
    for column in columns:
        cursor.execute(f'ALTER TABLE new_merged_data DROP COLUMN "{column}";')
    conn.commit()

    # Commit changes and close the connection

    cur.executescript('''
        ALTER TABLE new_merged_data DROP COLUMN id;
        ALTER TABLE new_merged_data DROP COLUMN primaryAccession;
        ALTER TABLE new_merged_data DROP COLUMN annotationScore;
        ALTER TABLE new_merged_data DROP COLUMN keywords;
        ALTER TABLE new_merged_data DROP COLUMN uniProtKBCrossReferences;
        ALTER TABLE new_merged_data DROP COLUMN seq_id;
        ALTER TABLE new_merged_data DROP COLUMN description;
        ALTER TABLE new_merged_data DROP COLUMN sequence;
        ALTER TABLE new_merged_data DROP COLUMN amino_count;
        ALTER TABLE new_merged_data DROP COLUMN "CTDC_#";
        ALTER TABLE new_merged_data DROP COLUMN "CTDD_#";
        ALTER TABLE new_merged_data DROP COLUMN "CTDT_#";
        ALTER TABLE new_merged_data DROP COLUMN "CTriad_#";
        ALTER TABLE new_merged_data DROP COLUMN "DPC_#";
        ALTER TABLE new_merged_data DROP COLUMN "GAAC_#";
        ALTER TABLE new_merged_data DROP COLUMN location_values;
        ALTER TABLE new_merged_data DROP COLUMN flexibility;
        ALTER TABLE new_merged_data DROP COLUMN secondary_structure_fraction;
        ALTER TABLE new_merged_data DROP COLUMN molar_extinction_coefficient;
        ALTER TABLE new_merged_data DROP COLUMN comments;
        ''')

    conn.commit()   

    # Close the connection
    conn.close()

    # delete all tsv files
    for tsv_filename in os.listdir(tsv_directory):
        if tsv_filename.endswith('.tsv'):
            os.remove(os.path.join(tsv_directory, tsv_filename))