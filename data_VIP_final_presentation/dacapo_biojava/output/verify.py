
def read_out_to_dict(filename):
    data = {}
    with open(filename, 'r') as f:

        header = f.readline().strip().split(',')
        
        current_sequence = ""
        current_values = []
        
        for line in f:
            line = line.strip()
            if not line:  
                continue
                
            if line.startswith(',') or line.startswith(' '): #if this line is a continuation of the previous line
                if current_values:
                    current_values.extend(value for value in line.split(',') if value)
            else:

                if current_sequence and current_values: 
                    properties = {}
                    for i in range(1, len(header)):  
                        if i < len(current_values):
                            properties[header[i]] = current_values[i]
                    data[current_sequence] = properties
                
                parts = line.split(',')
                current_sequence = parts[0].strip()
                current_values = parts
        
        if current_sequence and current_values: # Handle the last sequence
            properties = {}
            for i in range(1, len(header)):
                if i < len(current_values):
                    properties[header[i]] = current_values[i]
            data[current_sequence] = properties
            
    return data

def compare_sequences(biojava_file, optimized_file):
    bio_data = read_out_to_dict(biojava_file)

    opt_data = read_out_to_dict(optimized_file)

    # print(len(bio_data), len(opt_data))

    matching_sequences = []
    mismatched_sequences = []
    total_sequences = len(bio_data)
    mismatch_count = 0
    property_mismatches = {}

    for seq_name in bio_data:
        if seq_name in opt_data:

            is_match = True
            for prop in bio_data[seq_name]:
                if prop not in opt_data[seq_name]:
                    is_match = False
                    property_mismatches[seq_name] = f"Missing property: {prop}"
                    break
                    
                bio_val = bio_data[seq_name][prop]
                opt_val = opt_data[seq_name][prop]
                
                try:
                    bio_float = float(bio_val)
                    opt_float = float(opt_val)
                    if abs(bio_float - opt_float) > 0.0001:
                        is_match = False
                        property_mismatches[seq_name] = f"Value mismatch for {prop}: {bio_val} != {opt_val}"
                        break
                except ValueError:

                    if bio_val != opt_val:
                        is_match = False
                        property_mismatches[seq_name] = f"Value mismatch for {prop}: {bio_val} != {opt_val}"
                        break
            
            if is_match:
                matching_sequences.append(seq_name)
            else:
                mismatched_sequences.append(seq_name)
                mismatch_count += 1
        else:
            mismatched_sequences.append(seq_name)
            property_mismatches[seq_name] = "Sequence not found in optimized file"
            mismatch_count += 1

    print(f"Total sequences analyzed: {total_sequences}")
    print(f"Matching sequences: {len(matching_sequences)}")
    print(f"Mismatched sequences: {mismatch_count}")


    
    return matching_sequences, mismatched_sequences, property_mismatches

    return 0, 0, {}

if __name__ == "__main__":
    biojava_file = "biojava.out"
    optimized_file = "optimized_biojava.out"
    
    matching, mismatched, mismatches = compare_sequences(biojava_file, optimized_file)
    
    print("\nSample matching sequences:")
    for seq in matching[:5]:
        print(seq)
        
    print("\nSample mismatched sequences and reasons:")
    for seq in mismatched[:5]:
        print(f"{seq}: {mismatches.get(seq, 'Unknown reason')}")

