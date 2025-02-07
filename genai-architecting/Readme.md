## Functional Requirements

We are developing an AI-powered Japanese language tutor to assist students in learning and practicing Japanese. Due to concerns about data privacy and cost management, we aim to have a balance between leveraging cloud-based infrastructure and ensuring user data protection.

Unlike other implementations that rely on local AI hardware, we do not have the hardware to run models locally. Instead, we will utilize cloud-based services to host and deploy our AI models, ensuring scalability and accessibility.

## Assumptions

- Open-source LLMs will be used, hosted on cloud infrastructure.

- The cloud service must be cost-effective and support a student base of 300 users.

- Adequate network bandwidth and server capacity will be provisioned to ensure smooth interactions.

## Data Strategy

Copyrighted learning materials must be legally obtained and stored securely in a cloud database.

## Considerations

- Cloud providers such as AWS, Azure, or Google Cloud will be evaluated for hosting the AI model.

- [IBM Granite](https://huggingface.co/ibm-granite) is a potential option due to its fully open-source nature and transparent training data, which helps mitigate copyright concerns.

- Cost analysis for cloud hosting versus managed AI services will be conducted to ensure long-term sustainability.

## Risks

- Cloud service costs could scale unexpectedly with increased usage.

- Latency issues due to reliance on external infrastructure.