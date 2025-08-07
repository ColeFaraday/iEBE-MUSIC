#!/usr/bin/env python3

import h5py
import sys

def check_h5_structure(h5_file):
    """Check the structure of an h5 database"""
    try:
        with h5py.File(h5_file, 'r') as f:
            print(f"Root keys: {list(f.keys())}")
            
            if not list(f.keys()):
                print("No events found in database")
                return
                
            # Check first event
            first_event = list(f.keys())[0]
            print(f"\nFirst event: {first_event}")
            print(f"Files in first event:")
            
            event_group = f[first_event]
            for key in list(event_group.keys()):
                print(f"  - {key}")
                
            # Check if required files exist
            required_files = [
                "particle_9999_vndata_diff_eta_-0.5_0.5.dat",
                "particle_9999_pTeta_distribution.dat",
                "particle_9999_vndata_eta_-0.5_0.5.dat",
                "eccentricities_evo_ed_tau_0.4.dat"
            ]
            
            print(f"\nChecking for required files:")
            for req_file in required_files:
                if req_file in event_group:
                    print(f"  ✓ {req_file}")
                else:
                    print(f"  ✗ {req_file} (MISSING)")
                    
    except Exception as e:
        print(f"Error reading h5 file: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check_h5_structure.py <h5_file>")
        sys.exit(1)
        
    h5_file = sys.argv[1]
    check_h5_structure(h5_file) 