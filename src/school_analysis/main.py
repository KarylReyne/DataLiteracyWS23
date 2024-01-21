from school_analysis.plotting.general import GeneralPlots as gp
import subprocess



"""This is a dummy file to force poetry importing all subdirs as library"""
if __name__ == "__main__":

    if True:
        subprocess.check_call("poetry run src\school_analysis\download_all.py --keep-old")
    
    # gp.generate_SecEff_001_plots()
    gp.generate_SecEff_002_plots()
    # gp.generate_SecEff_003_plots()
