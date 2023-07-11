/* Scratch for reading ROOT files with a plain old ROOT macro.
3 July 2023. */

// #include "/net/cms17/cms17r0/schmitz/milliQanSim/include/mqROOTEvent.hh"
# include "/homes/anson/milliQanSim/include/mqROOTEvent.hh"
R__LOAD_LIBRARY(/net/cms17/cms17r0/schmitz/milliQanSim/build/libMilliQanCore.so)

void scratch_vanilla()
{
    std::unique_ptr<TFile> file( TFile::Open("/net/cms17/cms17r0/schmitz/slabSimMuon/withPhotons/48slab/cosmicdir1/MilliQan.root") );
    TTree *tree = file->Get<TTree>("Events");

    mqROOTEvent* event = new mqROOTEvent();
    tree->SetBranchAddress("ROOTEvent", &event);

    for (int i = 0; i < tree->GetEntries(); i++) {
        tree->GetEntry(i);
        cout << event->GetScintRHits()->front()->GetCopyNo() << endl;
        cout << event->GetEventEnergyDeposit() << endl;
    }
}