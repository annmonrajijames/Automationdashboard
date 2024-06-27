import sys

def main():
    if len(sys.argv) != 2:
        print("Usage: python test.py <input_file_path>")
        sys.exit(1)

    input_file_path = sys.argv[1]
    print(f"Processing file: {input_file_path}")
    # Add your code here to handle the input file

if __name__ == "__main__":
    main()
