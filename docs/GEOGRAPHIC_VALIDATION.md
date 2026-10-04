# GEOGRAPHIC VALIDATION
Primary: train Malihabad/Kakori/Mall → hold-out Rahimabad; preprocessing fit on train only. Plus GroupKFold by Orchard_ID (50 orchards, 400 rows each — correlated, not independent). Compare random vs grouped vs geo splits. Synthetic hold-out success ≠ real-world generalisation.
