#!/bin/bash
printf 'Do you want to:\n[1] Create a Bucket\n[2] Delete a Bucket\n'
read input

if [ $input = 1 ]
then
    printf '\nUsername: ' 
    read user

    # bucket management
    gsutil mb -p skona-tech-p1 -c NEARLINE -l US-EAST1 -b on gs://st-$user
    gsutil lifecycle set lifecyle.json gs://st-$user


    # account management
    gcloud iam service-accounts create $user \
        --description="" \
        --display-name="$user"

    gcloud projects add-iam-policy-binding skona-tech-p1 \
        --member="serviceAccount:$user@skona-tech-p1.iam.gserviceaccount.com" \
        --role="roles/storage.objectAdmin" \
        --condition="expression=resource.name.startsWith(\"projects/_/buckets/st-$user\"),title=st-$user,description="


    # key creation
    gcloud iam service-accounts keys create $user.json \
        --iam-account=$user@skona-tech-p1.iam.gserviceaccount.com
fi

if [ $input = 2 ]
then
    printf '\nUsername: '
    read user

    # bucket management
    gsutil -m rm -r gs://st-$user

    # iam permissions management
    gcloud projects remove-iam-policy-binding skona-tech-p1 \
        --member="serviceAccount:$user@skona-tech-p1.iam.gserviceaccount.com" \
        --role="roles/storage.objectAdmin" \
        --all

    # account management
    gcloud iam service-accounts delete $user@skona-tech-p1.iam.gserviceaccount.com
fi
