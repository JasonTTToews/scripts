# Scripts to handle repetitive and cumbersome tasks

## reset_commercetools.py
Given that Commercetools can have many dependencies, reseting a shop can be quite tedious, especially in dev or onboarding if an error occurred during Terraform or related operations. This script will remove all entities like products, product types, categories, stores, channels, etc from Commercetools and will manage all the dependencies as well.

#### !!!! IMPORTANT NOTE !!!!
Never run this on customer shops! This is only meant for personal shops, either for onboarding or working on the accelerator itself.
```
> python reset_commercetools.py <PROJECT_KEY> <CLIENT_ID> <CLIENT_SECRET>
```
