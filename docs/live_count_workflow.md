# Live Count Workflow

This guide is for election night operators running the MOE application.

## Pre-Election Preparation

### 1. Configure Election

1. Create or obtain the election configuration JSON:
   ```bash
   cp data/sample/election_config.json data/my_election/election_config.json
   ```
2. Edit `election_config.json` with the correct:
   - Electorate name, state, date
   - Candidate names, parties, and IDs
   - TCP candidate IDs (the two finalists)
   - Vote type estimates (from AEC enrolment data)

3. Set `DATA_DIR` in `.env`:
   ```
   DATA_DIR=data/my_election
   ```

### 2. Load Historical Data

1. Download 2022 booth results from the AEC
2. Format as `historical_booths.csv`:
   ```
   booth_id,alp_primary_pct,lib_primary_pct,grn_primary_pct,...,alp_tcp_pct,lib_tcp_pct
   ```
3. Place in `DATA_DIR`

### 3. Prepare Booth List

Create `booths.csv` with booth coordinates:
```
booth_id,booth_name,lat,lon,enrolled,division
```

Booth coordinates can be downloaded from the AEC polling place data.

### 4. Pre-Configure Preferences

Review and adjust default preference flows on the **Preference Model** page.

---

## Election Night Operations

### Phase 1: Polls Close (6:00 PM)

1. Launch the app:
   ```bash
   bash scripts/run.sh
   ```
2. Verify all sample data loads correctly (home page shows election metadata)
3. Navigate to **Live Count** page — confirm it shows "No votes counted yet"

### Phase 2: Early Count (6:00–8:00 PM)

The AEC begins distributing preliminary results from 6:15 PM (AEDT).

1. **Download** the booth results CSV from the AEC Virtual Tally Room
2. **Format** the CSV to match the `live_count.csv` schema
3. **Replace** `DATA_DIR/live_count.csv` with the updated file
4. Click **Refresh Data** in the app sidebar
5. Monitor the **Live Count** page for TCP margin updates

> ⚠️ Count status will show "early" until >25% is counted. Do not over-interpret early leads.

### Phase 3: Developing Count (8:00–10:00 PM)

1. Continue updating `live_count.csv` every 15–30 minutes
2. Update `declaration_votes.csv` with received counts as they come in
3. Check the **Swingometer** page for swing trends
4. Add commentary on the **Commentary** page

### Phase 4: Mature Count (10:00 PM+)

1. Run the Monte Carlo simulation on the **Prediction** page
2. Check recount risk on the **Live Count** page
3. Use the **Outstanding Votes Estimator** to project the final margin
4. If recount risk is "high" (margin < 100), flag for monitoring

### Phase 5: Declaration

1. The AEC will announce the result after all declaration votes are received (typically 2–3 weeks later)
2. Final results can be exported via the **Export** page

---

## Troubleshooting

| Problem | Solution |
|---|---|
| Data not loading | Check `DATA_DIR` in `.env`, verify CSV column names |
| Map not showing | Check folium/streamlit-folium installation |
| XLSX export fails | Ensure xlsxwriter is installed |
| Preference calculations wrong | Review pref flow matrix on Preference Model page |
